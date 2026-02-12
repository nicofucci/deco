import logging
import json
import socket
import struct
import time
import requests
from typing import List, Dict, Any
from scapy.all import ARP, Ether, srp, IP, UDP, DNS, DNSQR, sniff

logger = logging.getLogger("ndr_sensor")

class Fingerprinter:
    def __init__(self):
        self.oui_db = self._load_oui()

    def _load_oui(self):
        try:
            with open("app/oui_min.json", "r") as f:
                return json.load(f)
        except:
            return {}

    def get_vendor(self, mac: str) -> str:
        if not mac: return "Unknown"
        mac_clean = mac.replace(":", "").replace("-", "").upper()
        if len(mac_clean) < 6: return "Unknown"
        prefix = f"{mac_clean[0:2]}:{mac_clean[2:4]}:{mac_clean[4:6]}"
        return self.oui_db.get(prefix, "Unknown")

    def scan_mdns(self, timeout=8) -> List[Dict]:
        """
        Active mDNS scan using avahi-browse (safer in container).
        """
        results = []
        try:
            # avahi-browse -rt _workstation._tcp --parsable
            # But we want ALL services? -a
            # avahi-browse -art --parsable
            
            # Since we can't easily query generic active without daemon usually,
            # But avahi-utils works if dbus is mapped OR we use the standalone python implementation from block 3.
            # Block 3 used `avahi-browse`.
            # If the daemon is not running inside container (it isn't), avahi-browse might fail.
            # "Failed to create client object: Daemon not running" seen in logs in Block 3 options.
            
            # So scapy IS the way if no daemon.
            # But scapy crashed.
            
            # Implementation using pure socket multicast (active query) without scapy:
            return self._scan_mdns_socket(timeout)
            
        except Exception as e:
            logger.error(f"mDNS error: {e}")
            return []

    def _scan_mdns_socket(self, timeout):
        obs = []
        try:
            MCAST_GRP = '224.0.0.251'
            MCAST_PORT = 5353
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
            sock.settimeout(timeout)
            
            # Simple query for _services._dns-sd._udp.local matches scapy packet structure?
            # Creating manual DNS packet is hard without scapy.
            # Basic query payload for _services._dns-sd._udp.local (PTR)
            # Transaction ID: 0x0000
            # Flags: 0x0000 (Standard Query)
            # Questions: 1
            # Answer RRs: 0
            # Authority RRs: 0
            # Additional RRs: 0
            # Query: _services._dns-sd._udp.local
            
            # Hex payload for _services._dns-sd._udp.local PTR class IN
            # Header: 00 00 00 00 00 01 00 00 00 00 00 00
            # QNAME: 09 5f 73 65 72 76 69 63 65 73 07 5f 64 6e 73 2d 73 64 04 5f 75 64 70 05 6c 6f 63 61 6c 00
            # QTYPE: 00 0c (PTR)
            # QCLASS: 00 01 (IN)
            
            payload = b'\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00' \
                      b'\x09_services\x07_dns-sd\x04_udp\x05local\x00' \
                      b'\x00\x0c\x00\x01'
            
            try:
                sock.sendto(payload, (MCAST_GRP, MCAST_PORT))
            except Exception as s_err:
                 logger.warning(f"mDNS send failed: {s_err}")
                 # continue to listen anyway?
            
            start = time.time()
            while time.time() - start < timeout:
                try:
                    data, addr = sock.recvfrom(65535)
                    # We got a response. Just log it for now or try to extract names.
                    # Parsing DNS packet manually is tedious.
                    # We can use dnslib if installed, but it's not.
                    # We can use simple string matching for known patterns (e.g. valid chars).
                    
                    # Extract readable strings
                    raw_str = data.decode('utf-8', errors='ignore')
                    # Look for strings like "Chromecast", "Apple TV", etc.
                    # Or "_googlecast", "_airplay"
                    
                    names = []
                    lower = raw_str.lower()
                    if "_airplay" in lower: names.append("_airplay")
                    if "_googlecast" in lower: names.append("_googlecast")
                    if "_ipp" in lower: names.append("_ipp")
                    if "workstation" in lower: names.append("Workstation")
                    
                    # Also try to grab the first "Name" like string? Too risky.
                    
                    if names:
                        obs.append({
                            "ip": addr[0],
                            "names": names,
                            "type": "mdns_services",
                            "source": "mdns"
                        })
                except socket.timeout:
                    break
        except Exception as e:
            logger.error(f"mDNS Socket Error: {e}")
        finally:
             try: sock.close()
             except: pass
        return obs


    def scan_ssdp(self, timeout=5) -> List[Dict]:
        """
        SSDP Discovery (already implemented in scanner_passive, reusing logic or enhancing)
        """
        results = []
        group = ("239.255.255.250", 1900)
        message = "\r\n".join([
            'M-SEARCH * HTTP/1.1',
            'HOST: 239.255.255.250:1900',
            'MAN: "ssdp:discover"',
            'ST: ssdp:all',
            'MX: 3',
            '', ''
        ])
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.settimeout(timeout)
        try:
            sock.sendto(message.encode(), group)
            
            start = time.time()
            while time.time() - start < timeout:
                try:
                    data, addr = sock.recvfrom(1024)
                    header_str = data.decode("utf-8", errors="ignore")
                    headers = {}
                    for line in header_str.split("\r\n"):
                        if ":" in line:
                            k, v = line.split(":", 1)
                            headers[k.strip().upper()] = v.strip()
                            
                    results.append({
                        "ip": addr[0],
                        "server": headers.get("SERVER", ""),
                        "location": headers.get("LOCATION", ""),
                        "usn": headers.get("USN", ""),
                        "st": headers.get("ST", "")
                    })
                except socket.timeout:
                    break
        except Exception as e:
            pass
        finally:
            sock.close()
            
        return results

    def banner_grab(self, ip: str, ports=[80, 443]) -> Dict:
        """
        Simple Banner Grabbing
        """
        banners = {}
        for port in ports:
            proto = "https" if port == 443 else "http"
            try:
                resp = requests.head(f"{proto}://{ip}", timeout=1.0, verify=False)
                banners[port] = {
                    "server": resp.headers.get("Server"),
                    "x-powered-by": resp.headers.get("X-Powered-By"),
                    "title": "" # simplistic
                }
            except:
                pass
        return banners
