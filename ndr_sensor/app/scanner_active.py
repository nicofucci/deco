
import subprocess
import re
import logging
import shutil
import json
import ipaddress
import time
from typing import List, Dict, Any, Tuple, Optional
from app.fingerprinting import Fingerprinter

logger = logging.getLogger("ndr_sensor")

class ActiveScanner:
    def __init__(self):
        self.arp_scan_path = shutil.which("arp-scan")
        self.nmap_path = shutil.which("nmap")
        self.primary_iface = None
        self.primary_cidr = None
        self.primary_ip = None
        self.fingerprinter = Fingerprinter()
        
        # Initial Detection
        self.pick_primary_lan_interface()

    def pick_primary_lan_interface(self) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Detects the real LAN interface, excluding docker, loopback, etc.
        Returns: (iface, cidr, ip)
        """
        try:
            # Get default route interface first
            default_iface = None
            try:
                route_cmd = ["ip", "-j", "route", "show", "default"]
                route_out = subprocess.check_output(route_cmd, text=True)
                routes = json.loads(route_out)
                if routes and "dev" in routes[0]:
                    default_iface = routes[0]["dev"]
            except Exception as e:
                logger.warning(f"Could not get default route: {e}")

            # Get all addresses
            addr_cmd = ["ip", "-j", "addr"]
            addr_out = subprocess.check_output(addr_cmd, text=True)
            ifaces = json.loads(addr_out)
            
            candidate = None
            
            for iface in ifaces:
                name = iface.get("ifname", "")
                
                # Exclusions
                if name == "lo": continue
                if name.startswith("docker"): continue
                if name.startswith("br-"): continue
                if name.startswith("veth"): continue
                if name.startswith("cni"): continue
                if name.startswith("flannel"): continue
                if name.startswith("tun"): continue
                if name.startswith("tap"): continue
                if name.startswith("vmnet"): continue
                if name.startswith("wg"): continue
                if name.startswith("nordlynx"): continue
                
                # Check addresses
                for addr_info in iface.get("addr_info", []):
                    if addr_info.get("family") == "inet":
                        ip_str = addr_info.get("local")
                        prefix_len = addr_info.get("prefixlen")
                        
                        try:
                            ip_obj = ipaddress.IPv4Address(ip_str)
                            # Prefer RFC1918 Private
                            if ip_obj.is_private:
                                current_cand = (name, f"{ip_str}/{prefix_len}", ip_str)
                                
                                # If matches default route, it is the winner
                                if default_iface and name == default_iface:
                                    self.primary_iface, self.primary_cidr, self.primary_ip = current_cand
                                    logger.info(f"LAN DETECTED (Result): IFACE={name} IP={ip_str} CIDR={self.primary_cidr}")
                                    return current_cand
                                
                                # Otherwise keep as candidate
                                if not candidate:
                                    candidate = current_cand
                        except:
                            pass
            
            # Fallback to candidate if default route match not found
            if candidate:
                self.primary_iface, self.primary_cidr, self.primary_ip = candidate
                logger.info(f"LAN DETECTED (Fallback): IFACE={self.primary_iface} IP={self.primary_ip} CIDR={self.primary_cidr}")
                return candidate
                
        except Exception as e:
            logger.error(f"Failed to detect LAN interface: {e}")
            
        return None, None, None

    def run_scan(self, cidr: str, mode: str = "fast") -> List[Dict[str, Any]]:
        target_cidr = cidr
        if self.primary_cidr and (cidr == "192.168.100.0/24" and "192.168.100" not in self.primary_cidr):
            pass

        logger.info(f"Running Scan on {target_cidr} (Mode: {mode})")
        observations = []
        discovered_ips = set()
        ip_mac_map = {} # IP -> MAC

        # 1. Discovery Phase
        # -------------------
        
        # A) IP Neigh
        logger.debug("Running IP Neigh...")
        neigh_obs = self._run_ip_neigh()
        for o in neigh_obs:
            observations.append(o)
            discovered_ips.add(o['ip'])
            if o.get('mac'): ip_mac_map[o['ip']] = o['mac']

        # B) Ping Sweep
        logger.debug("Running Nmap Ping Sweep...")
        ping_obs = self._run_nmap_ping_sweep(target_cidr)
        for o in ping_obs:
            observations.append(o)
            discovered_ips.add(o['ip'])

        # C) ARP Scan
        if self.arp_scan_path:
            logger.debug("Running ARP Scan...")
            iface_arg = self.primary_iface
            arp_obs = self._run_arp_scan(target_cidr, iface_arg)
            for o in arp_obs:
                observations.append(o)
                discovered_ips.add(o['ip'])
                if o.get('mac'): ip_mac_map[o['ip']] = o['mac']
        
        # 1.5 Gateway Interrogation (SNMP/ARP Leases)
        try:
            logger.info("Attempting Gateway Detection...")
            route_out = subprocess.check_output(["ip", "route"], text=True)
            logger.debug(f"Route raw: {route_out}")
            
            gateway_ip = None
            for line in route_out.splitlines():
                if "default via" in line:
                    parts = line.split()
                    if len(parts) >= 3:
                        gateway_ip = parts[2]
                        logger.info(f"Found Gateway IP: {gateway_ip}")
                        break
            
            if gateway_ip:
                logger.info(f"Interrogating Gateway: {gateway_ip}")
                from app.scanner_gateway import GatewayScanner
                gw_scanner = GatewayScanner()
                gw_obs = gw_scanner.scan_gateway_snmp(gateway_ip)
                if gw_obs:
                     logger.info(f"Gateway SNMP yielded {len(gw_obs)} records")
                     for o in gw_obs:
                         observations.append(o)
                         discovered_ips.add(o['ip'])
                         # Update MAC map to help fingerprinting
                         if o.get('mac'): ip_mac_map[o['ip']] = o['mac']
            else:
                logger.warning("No default gateway found in routes")
        except Exception as e:
            logger.warning(f"Gateway Interrogation failed: {e}")

        # 2. Fingerprinting Phase
        # ------------------------
        logger.info(f"Starting Fingerprinting on {len(discovered_ips)} hosts...")
        
        # D) mDNS (Active Query) -> Multicast, affects all
        # We run this once regardless of discovered IPs, as it listens for responses
        mdns_results = self.fingerprinter.scan_mdns(timeout=4) # Short timeout for speed
        for res in mdns_results:
             observations.append({
                 "ip": res.get("ip"),
                 "names": res.get("names", []),
                 "type": "mdns_services", # internal type
                 "source": "mdns",
                 "confidence_delta": 30,
                 "raw_text": str(res)
             })
             if res.get("ip"): discovered_ips.add(res.get("ip"))

        # E) SSDP (Active Query)
        ssdp_results = self.fingerprinter.scan_ssdp(timeout=4)
        for res in ssdp_results:
             observations.append({
                 "ip": res.get("ip"),
                 "server": res.get("server"),
                 "st": res.get("st"),
                 "usn": res.get("usn"),
                 "location": res.get("location"),
                 "source": "ssdp",
                 "confidence_delta": 25,
                 "raw_text": str(res)
             })
             if res.get("ip"): discovered_ips.add(res.get("ip"))
             
        # F) Per-Host Checks (OUI + Banner)
        # Using discovered IPs list
        for ip in discovered_ips:
            # OUI
            mac = ip_mac_map.get(ip)
            if mac:
                vendor = self.fingerprinter.get_vendor(mac)
                if vendor != "Unknown":
                    observations.append({
                        "ip": ip,
                        "mac": mac,
                        "vendor": vendor,
                        "source": "oui",
                        "confidence_delta": 10,
                        "raw_text": f"OUI Match: {vendor}"
                    })
            
            # Banner Grab
            # Only doing 80/443 quick check
            banners = self.fingerprinter.banner_grab(ip)
            if banners:
                 observations.append({
                     "ip": ip,
                     "headers": banners,
                     "source": "banner_http",
                     "confidence_delta": 20,
                     "raw_text": json.dumps(banners)
                 })

        # G) Nmap Full (if mode=full)
        if mode == "full" and self.nmap_path and discovered_ips:
             nmap_full_obs = self._run_nmap_full(list(discovered_ips))
             observations.extend(nmap_full_obs)

        return observations

    def _run_ip_neigh(self) -> List[Dict[str, Any]]:
        results = []
        try:
            cmd = ["ip", "-j", "neigh", "show"]
            output = subprocess.check_output(cmd, text=True)
            entries = json.loads(output)
            
            for entry in entries:
                state = entry.get("state", [])
                if any(s in state for s in ["REACHABLE", "STALE", "DELAY", "PROBE"]):
                    ip = entry.get("dst")
                    mac = entry.get("lladdr")
                    if ip and mac:
                        results.append({
                            "ip": ip,
                            "mac": mac,
                            "vendor": "Unknown",
                            "source": "ndr_ip_neigh",
                            "confidence_delta": 25,
                            "raw_text": str(entry)
                        })
        except Exception as e:
            logger.error(f"IP Neigh failed: {e}")
        return results

    def _run_nmap_ping_sweep(self, cidr: str) -> List[Dict[str, Any]]:
        results = []
        # nmap -sn -PR -PE --min-parallelism 20 --max-retries 1 <cidr>
        cmd = ["nmap", "-sn", "-PR", "-PE", "--min-parallelism", "20", "--max-retries", "1", "-oG", "-", cidr]
        try:
            output = subprocess.check_output(cmd, text=True)
            for line in output.splitlines():
                if "Status: Up" in line:
                    # Host: 192.168.100.1 ()	Status: Up
                    ip_match = re.search(r"Host: ([\d\.]+) ", line)
                    if ip_match:
                        results.append({
                            "ip": ip_match.group(1),
                            "mac": None, # Ping sweep often doesn't give MAC unless local root
                            "source": "ndr_nmap_ping",
                            "confidence_delta": 20,
                            "raw_text": line
                        })
        except Exception as e:
            logger.error(f"Nmap Ping Sweep failed: {e}")
        return results

    def _run_arp_scan(self, cidr: str, iface: str = None) -> List[Dict[str, Any]]:
        results = []
        try:
            cmd = ["arp-scan", "--plain", "--ignoredups"]
            if iface:
                cmd.extend(["--interface", iface])
            
            # If we have an interface, arp-scan --localnet is often better/easier than CIDR 
            # if we want to scan the whole local segment.
            # But instruction says "arp-scan --interface=<lan_iface> --localnet"
            if iface:
               cmd.append("--localnet")
            else:
               cmd.append(cidr)

            # Need stderr pipe to ignore warnings
            process = subprocess.run(cmd, capture_output=True, text=True)
            if process.returncode != 0 and "pcap_activate" in process.stderr:
                 logger.error(f"arp-scan permission error: {process.stderr}")
                 return []
            
            output = process.stdout
            for line in output.splitlines():
                parts = line.split()
                if len(parts) >= 2:
                    ip = parts[0]
                    mac = parts[1]
                    vendor = " ".join(parts[2:]) if len(parts) > 2 else "Unknown"
                    results.append({
                        "ip": ip,
                        "mac": mac,
                        "vendor": vendor,
                        "source": "ndr_active_arp",
                        "confidence_delta": 40,
                        "raw_text": line
                    })
        except Exception as e:
            logger.error(f"ARP Scan failed: {e}")
        return results

    def _run_nmap_full(self, ips: List[str]) -> List[Dict[str, Any]]:
        results = []
        # -sS -sV --top-ports 100 -T4 --open
        # Batching IPs? Assuming list isn't huge.
        cmd = ["nmap", "-sS", "-sV", "--top-ports", "100", "-T4", "--open", "-oG", "-"] + ips
        
        try:
            process = subprocess.run(cmd, capture_output=True, text=True)
            output = process.stdout
            
            current_ip = None
            
            for line in output.splitlines():
                 if "Status: Up" in line: continue
                 if "Ports:" in line:
                    ip_match = re.search(r"Host: ([\d\.]+) ", line)
                    if ip_match:
                        ip = ip_match.group(1)
                        ports_raw = re.findall(r"(\d+)/open/tcp//([^/]*)/", line)
                        ports_list = [{"port": p[0], "service": p[1]} for p in ports_raw]
                        if ports_list:
                            results.append({
                                "ip": ip,
                                "mac": None, 
                                "ports": ports_list,
                                "source": "ndr_nmap_full",
                                "confidence_delta": 30, # Confirms it has open ports
                                "raw_text": line
                            })
        except Exception as e:
            logger.error(f"Nmap Full Scan failed: {e}")
        return results
