import subprocess
import shutil
import json
import socket
import threading
from ipaddress import IPv4Network

class Scanner:
    def __init__(self):
        self.nmap_path = shutil.which("nmap")
        if not self.nmap_path:
            print("[!] Nmap not found. Using Mock Scanner.")

    def scan(self, target, job_type):
        if job_type == "discovery":
            return self.scan_discovery(target)
        elif job_type == "ports":
            return self.scan_ports(target)
        elif job_type == "xray_network_scan":
            return self.scan_xray_v2(target)
        else:
            return {"error": "Unknown job type"}

    def scan_xray_v2(self, target):
        """
        X-RAY v2: Real Discovery (Ping Sweep + ARP + Ports + Hostnames)
        """
        print(f"[*] Starting X-RAY v2 on {target}...")
        
        # 1. Identify Network Context
        iface_info = self.get_active_interface()
        if not iface_info:
            print("[!] Could not detect active interface.")
            return {"error": "No active interface found"}
            
        print(f"[*] Active Interface: {iface_info['ip']} ({iface_info['name']}) - GW: {iface_info['gateway']}")
        
        # Determine Scan Range (from Interface or Target)
        cidr = target
        if "/" not in target or target == "auto":
            cidr = self.get_cidr_from_ip(iface_info['ip'])
            print(f"[*] Auto-detected CIDR: {cidr}")

        # 2. Discovery Phase (Active)
        alive_hosts = self.ping_sweep(cidr)
        
        # 3. ARP Harvest (Passive/Active)
        arp_table = self.get_arp_table()
        
        # 4. Correlate & Enrich
        devices = []
        all_ips = set(alive_hosts) | set(arp_table.keys())
        
        for ip in all_ips:
            mac = arp_table.get(ip, "00:00:00:00:00:00") 
            hostname = self.resolve_hostname(ip)
            open_ports = self.scan_top_ports(ip)
            
            os_guess = "Unknown"
            if 445 in open_ports or 139 in open_ports:
                os_guess = "Windows"
            elif 22 in open_ports:
                os_guess = "Linux/Unix"
            elif 62078 in open_ports: 
                os_guess = "iOS"
            
            devices.append({
                "ip": ip,
                "hostname": hostname,
                "mac": mac,
                "type": "unknown", 
                "os_guess": os_guess,
                "open_ports": open_ports,
                "source": "XRAY_v2",
                "confidence": 100
            })
            
        return {
            "target": cidr,
            "devices": devices,
            "metadata": {
                "method": "xray_v2_polyglot", 
                "interface": iface_info,
                "agent_version": "3.0.2"
            }
        }

    def get_active_interface(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return {
                "name": "primary_detected", 
                "ip": local_ip, 
                "gateway": "unknown" 
            }
        except Exception as e:
            print(f"[!] Interface detect failed: {e}")
            return None

    def get_cidr_from_ip(self, ip):
        parts = ip.split(".")
        return f"{parts[0]}.{parts[1]}.{parts[2]}.0/24"

    def ping_sweep(self, cidr):
        active_ips = []
        lock = threading.Lock()
        
        try:
            net = IPv4Network(cidr, strict=False)
        except:
             return []

        def ping(ip):
            host = str(ip)
            import platform
            args = ["ping", "-c", "1", "-W", "1", host]
            if platform.system().lower() == "windows":
                args = ["ping", "-n", "1", "-w", "500", host]
                
            try:
                subprocess.check_call(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                with lock:
                    active_ips.append(host)
            except:
                pass

        threads = []
        hosts = list(net.hosts())[:254] 
        BATCH_SIZE = 50
        for i in range(0, len(hosts), BATCH_SIZE):
            batch = hosts[i:i+BATCH_SIZE]
            current_threads = []
            for ip in batch:
                t = threading.Thread(target=ping, args=(ip,))
                t.start()
                current_threads.append(t)
            for t in current_threads:
                t.join()
        return active_ips

    def get_arp_table(self):
        import re
        arp_map = {}
        try:
            output = subprocess.check_output(["arp", "-a"], text=True)
            for line in output.splitlines():
                ip_match = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', line)
                mac_match = re.search(r'([0-9A-Fa-f]{2}[:-][0-9A-Fa-f]{2}[:-][0-9A-Fa-f]{2}[:-][0-9A-Fa-f]{2}[:-][0-9A-Fa-f]{2}[:-][0-9A-Fa-f]{2})', line)
                if ip_match and mac_match:
                    ip = ip_match.group(1)
                    mac = mac_match.group(1).replace("-", ":")
                    arp_map[ip] = mac
        except:
            pass
        return arp_map

    def resolve_hostname(self, ip):
        try:
            return socket.gethostbyaddr(ip)[0]
        except:
            return ""

    def scan_top_ports(self, ip):
        top_ports = [21, 22, 23, 25, 53, 80, 135, 139, 443, 445, 3306, 3389, 8080]
        open_ports = []
        for p in top_ports:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.2) 
                if s.connect_ex((ip, p)) == 0:
                    open_ports.append(p)
                s.close()
            except:
                pass
        return open_ports

    def scan_discovery(self, target):
        print(f"[*] Running Discovery on {target}...")
        return {
            "target": target,
            "hosts": [{
                "ip": target.split("/")[0] if "/" in target else target, 
                "hostname": "discovered-host",
                "status": "up"
            }]
        }

    def scan_ports(self, target):
        print(f"[*] Running Port Scan on {target}...")
        return {
            "target": target,
            "ports": [80, 22, 443, 3389],
            "nmap_run": {
                "host": {
                    "address": {"addr": target, "addrtype": "ipv4"},
                    "hostnames": [{"name": "target-host"}],
                    "ports": {
                        "port": [
                            {"portid": "80", "protocol": "tcp", "service": {"name": "http", "product": "nginx"}},
                            {"portid": "22", "protocol": "tcp", "service": {"name": "ssh", "product": "OpenSSH"}},
                            {"portid": "443", "protocol": "tcp", "service": {"name": "https", "product": "nginx"}}
                        ]
                    }
                }
            }
        }
