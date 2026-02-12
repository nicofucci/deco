import logging
import subprocess
import socket
import struct
import time
from typing import List, Dict, Any

logger = logging.getLogger("ndr_sensor")

class PassiveScanner:
    def scan(self, duration: int = 30) -> List[Dict[str, Any]]:
        observations = []
        
        # 1. mDNS (Avahi-browse)
        logger.info("Running Passive: mDNS")
        mdns = self._scan_mdns(duration=min(duration, 10))
        observations.extend(mdns)
        
        # 2. SSDP (Python socket)
        logger.info("Running Passive: SSDP")
        ssdp = self._scan_ssdp(duration=min(duration, 5))
        observations.extend(ssdp)
        
        # 3. DHCP Sniffer (Passive)
        logger.info("Running Passive: DHCP Sniffer")
        dhcp_obs = self._listen_dhcp(duration=min(duration, 15))
        observations.extend(dhcp_obs)

        return observations

    def _scan_mdns(self, duration: int) -> List[Dict[str, Any]]:
        results = []
        MCAST_GRP = '224.0.0.251'
        MCAST_PORT = 5353
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            sock.bind(('', MCAST_PORT))
            mreq = struct.pack("4sl", socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
            sock.settimeout(1.0)
            
            logger.info(f"Listening for Passive mDNS on {MCAST_GRP}:{MCAST_PORT} for {duration}s")
            start = time.time()
            
            processed_ips = set()

            while time.time() - start < duration:
                try:
                    data, addr = sock.recvfrom(10240)
                    ip = addr[0]
                    
                    # Basic DNS Header Check
                    # ID(2), Flags(2), QDCOUNT(2), ANCOUNT(2) ...
                    if len(data) < 12: continue
                    
                    # We care about Answers (ANCOUNT > 0)
                    ancount = int.from_bytes(data[6:8], 'big')
                    if ancount == 0: continue
                    
                    # Naive string search for services if parsing is too complex without DNSEslib
                    # We look for common service strings in the payload
                    payload = data.decode('utf-8', 'ignore')
                    
                    services = []
                    if "_googlecast._tcp" in payload: services.append("Chromecast")
                    if "_airplay._tcp" in payload: services.append("AirPlay")
                    if "_spotify-connect" in payload: services.append("Spotify")
                    if "_printer._tcp" in payload: services.append("Printer")
                    if "_smb._tcp" in payload: services.append("File Share")
                    
                    if services:
                        raw_desc = ", ".join(services)
                        results.append({
                            "ip": ip,
                            "hostname": "", # Hard to extract without full DNS parsing
                            "vendor": "",
                            "source": "ndr_passive_mdns",
                            "confidence_delta": 20,
                            "raw_text": f"Passive mDNS: Detected {raw_desc}"
                        })

                except socket.timeout:
                    continue
                except Exception as e:
                    pass
        except Exception as e:
            logger.error(f"Passive mDNS Error: {e}")
        finally:
            sock.close()
            
        return results

    def _listen_dhcp(self, duration: int) -> List[Dict[str, Any]]:
        results = []
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.settimeout(1.0) # Short timeout for loop
            try:
                sock.bind(('0.0.0.0', 67))
            except PermissionError:
                logger.warning("DHCP Sniffing requires root privileges (port 67)")
                return []
            except Exception as e:
                logger.warning(f"DHCP Bind failed: {e}")
                return []

            logger.info(f"Listening for DHCP on 0.0.0.0:67 for {duration}s")
            start_time = time.time()
            
            while time.time() - start_time < duration:
                try:
                    data, addr = sock.recvfrom(2048)
                    # Simple BOOTP parsing
                    # Op(1), Htype(1), Hlen(1), Hops(1), Xid(4), Secs(2), Flags(2), Ciaddr(4), Yiaddr(4), Siaddr(4), Giaddr(4), Chaddr(16)
                    if len(data) < 240: continue
                    
                    # Magic Cookie 0x63825363
                    if data[236:240] != b'\x63\x82\x53\x63': continue
                    
                    # Parse Options
                    options = data[240:]
                    idx = 0
                    dhcp_info = {"ip": addr[0]}
                    hostname = None
                    vendor = None
                    msg_type = None

                    while idx < len(options):
                        opt_code = options[idx]
                        if opt_code == 255: break # End
                        if opt_code == 0: 
                            idx += 1
                            continue
                            
                        opt_len = options[idx+1]
                        opt_val = options[idx+2:idx+2+opt_len]
                        
                        if opt_code == 53: # Msg Type
                            msg_type = int.from_bytes(opt_val, 'big')
                        elif opt_code == 12: # Hostname
                            hostname = opt_val.decode('utf-8', 'ignore')
                        elif opt_code == 60: # Vendor Class ID
                            vendor = opt_val.decode('utf-8', 'ignore')
                        
                        idx += 2 + opt_len

                    if hostname or vendor:
                         results.append({
                            "ip": "0.0.0.0", # DHCP Request often from 0.0.0.0, we rely on Chaddr for MAC if needed, but Orchestrator needs IP/MAC
                            # We can extract MAC from Chaddr
                            "mac": ':'.join('%02x' % b for b in data[28:34]),
                            "hostname": hostname,
                            "vendor": vendor,
                            "source": "ndr_passive_dhcp",
                            "confidence_delta": 40,
                            "raw_text": f"DHCP Type {msg_type}: Host={hostname} Vendor={vendor}"
                        })

                except socket.timeout:
                    continue
                except Exception as e:
                    logger.error(f"DHCP Packet Parse Error: {e}")
                    
        except Exception as e:
            logger.error(f"DHCP Sniffer Error: {e}")
        finally:
            try: sock.close()
            except: pass
            
        return results

    def _scan_ssdp(self, duration: int) -> List[Dict[str, Any]]:
        results = []
        try:
            # avahi-browse -a -r -p -t
            # -a all, -r resolve, -p parsable, -t terminate
            cmd = ["avahi-browse", "-a", "-r", "-p", "-t"]
            # Timed execution can be tricky if -t doesn't work well without daemon
            # We assume avahi-daemon is NOT running inside docker? avahi-utils might need dbus.
            # If standard tools fail, we skip.
            output = subprocess.check_output(cmd, text=True, timeout=duration+5)
            for line in output.splitlines():
                if line.startswith("="):
                    # =;eth0;IPv4;MyPhone;_googlecast._tcp;local;192.168.100.105;8009;"fn=..."
                    parts = line.split(";")
                    if len(parts) >= 7:
                        ip = parts[7]
                        hostname = parts[3]
                        results.append({
                            "ip": ip,
                            "hostname": hostname,
                            "source": "ndr_passive_mdns",
                            "confidence_delta": 15,
                            "raw_text": line
                        })
        except Exception:
            pass
        return results

    def _scan_ssdp(self, duration: int) -> List[Dict[str, Any]]:
        results = []
        SSDP_ADDR = "239.255.255.250"
        SSDP_PORT = 1900
        SSDP_MX = 1
        SSDP_ST = "ssdp:all"

        ssdpRequest = "M-SEARCH * HTTP/1.1\r\n" + \
                    "HOST: {}:{}\r\n".format(SSDP_ADDR, SSDP_PORT) + \
                    "MAN: \"ssdp:discover\"\r\n" + \
                    "MX: {}\r\n".format(SSDP_MX) + \
                    "ST: {}\r\n".format(SSDP_ST) + \
                    "\r\n"

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(duration)
        try:
            sock.sendto(ssdpRequest.encode(), (SSDP_ADDR, SSDP_PORT))
            start = time.time()
            while time.time() - start < duration:
                try:
                    data, addr = sock.recvfrom(1024)
                    ip = addr[0]
                    # Parse simplified USN/Server
                    raw = data.decode('utf-8', errors='ignore')
                    results.append({
                        "ip": ip,
                        "source": "ndr_passive_ssdp",
                        "confidence_delta": 10,
                        "raw_text": raw[:100]
                    })
                except socket.timeout:
                    break
        except Exception:
            pass
        finally:
            sock.close()
        return results
