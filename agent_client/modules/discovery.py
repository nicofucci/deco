import subprocess
import platform
import logging
import socket
from concurrent.futures import ThreadPoolExecutor
import ipaddress

logger = logging.getLogger(__name__)

class NetworkDiscovery:
    def __init__(self):
        self.os_type = platform.system()
        # Puertos que queremos comprobar cuando hagamos full/ports por host
        self.common_ports = [21, 22, 23, 25, 53, 80, 110, 135, 139, 143, 443, 445, 3306, 3389, 5432, 8080]

    def ping(self, ip):
        param = '-n' if self.os_type == 'Windows' else '-c'
        command = ['ping', param, '1', ip]
        
        try:
            # Hide window on Windows
            startupinfo = None
            if self.os_type == 'Windows':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                
            response = subprocess.call(
                command, 
                stdout=subprocess.DEVNULL, 
                stderr=subprocess.DEVNULL,
                startupinfo=startupinfo
            )
            return ip if response == 0 else None
        except Exception as e:
            logger.error(f"Ping failed for {ip}: {e}")
            return None

    def _ping_sweep(self, cidr: str):
        """
        Hace ping concurrente a todos los hosts de una red CIDR.
        Devuelve lista de IPs que respondieron.
        """
        alive = []
        try:
            network = ipaddress.ip_network(cidr, strict=False)
        except Exception as e:
            logger.error(f"CIDR inválido {cidr}: {e}")
            return []

        # Excluir network/broadcast en IPv4
        hosts = list(network.hosts())
        if len(hosts) > 1024:
            # Evitamos barridos gigantes; limitamos a 1024 hosts por seguridad.
            hosts = hosts[:1024]
            logger.warning(f"Red grande, limitando a primeros 1024 hosts: {cidr}")

        with ThreadPoolExecutor(max_workers=64) as executor:
            futures = {executor.submit(self.ping, str(ip)): str(ip) for ip in hosts}
            for future in futures:
                ip = future.result()
                if ip:
                    alive.append(ip)
        return alive

    def scan_network(self, target: str):
        """
        Descubre hosts vivos en una red.
        - Si target es IP sin CIDR, devuelve esa IP si responde a ping.
        - Si es CIDR, hace ping sweep.
        """
        try:
            if "/" in target:
                return self._ping_sweep(target)
            else:
                single = self.ping(target)
                return [single] if single else []
        except Exception as e:
            logger.error(f"scan_network error: {e}")
            return []

    def get_network_info(self):
        info = {
            "local_ip": None,
            "primary_cidr": None,
            "interfaces": []
        }
        
        # 1. Get Local IP (Primary)
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            info["local_ip"] = s.getsockname()[0]
            s.close()
        except Exception:
            try:
                info["local_ip"] = socket.gethostbyname(socket.gethostname())
            except:
                pass

        # 2. Get Interfaces and CIDR
        try:
            if self.os_type == "Linux":
                self._get_linux_network_info(info)
            elif self.os_type == "Windows":
                self._get_windows_network_info(info)
        except Exception as e:
            logger.error(f"Error getting network info: {e}")

        return info

    def _get_linux_network_info(self, info):
        import json
        import struct
        try:
            # Try ip -j addr first
            output = subprocess.check_output(["ip", "-j", "addr"], text=True)
            interfaces = json.loads(output)
            
            for iface in interfaces:
                name = iface.get("ifname")
                if name == "lo": continue
                
                for addr_info in iface.get("addr_info", []):
                    if addr_info.get("family") == "inet":
                        ip = addr_info.get("local")
                        prefixlen = addr_info.get("prefixlen")
                        
                        # Calculate network
                        host_bits = 32 - prefixlen
                        netmask = (0xFFFFFFFF >> host_bits) << host_bits
                        ip_int = struct.unpack("!I", socket.inet_aton(ip))[0]
                        network_int = ip_int & netmask
                        network_ip = socket.inet_ntoa(struct.pack("!I", network_int))
                        network_cidr = f"{network_ip}/{prefixlen}"

                        iface_data = {"name": name, "ip": ip, "cidr": network_cidr}
                        info["interfaces"].append(iface_data)
                        
                        if ip == info["local_ip"]:
                            info["primary_cidr"] = network_cidr
        except Exception as e:
            logger.error(f"Linux network discovery failed: {e}")

    def _get_windows_network_info(self, info):
        # Basic parsing of ipconfig
        # This is a best-effort implementation for Windows without external deps
        try:
            import re
            output = subprocess.check_output(["ipconfig"], text=True)
            
            current_iface = None
            # Regex for IPv4 Address. . . . . . . . . . . : 192.168.1.34
            # Regex for Subnet Mask . . . . . . . . . . . : 255.255.255.0
            
            lines = output.splitlines()
            for line in lines:
                if not line.strip(): continue
                
                if "adapter" in line.lower():
                    current_iface = line.split("adapter")[1].strip().rstrip(":")
                    continue
                
                if "IPv4" in line or "IP Address" in line:
                    parts = line.split(":")
                    if len(parts) > 1:
                        ip = parts[1].strip()
                        # We need the mask to calculate CIDR, so we store IP temporarily
                        # But ipconfig output order is usually IP then Mask.
                        # Let's look ahead or store state.
                        # Simpler: just grab the IP and if it matches local_ip, try to find mask in next lines
                        pass 

            # Re-implementing with a more robust approach using PowerShell if available
            # PowerShell Get-NetIPAddress is much better
            cmd = ["powershell", "-Command", "Get-NetIPAddress -AddressFamily IPv4 | Select-Object IPAddress, InterfaceAlias, PrefixLength | ConvertTo-Json"]
            output = subprocess.check_output(cmd, text=True)
            import json
            data = json.loads(output)
            if isinstance(data, dict): data = [data] # Handle single result
            
            for item in data:
                ip = item.get("IPAddress")
                prefix = item.get("PrefixLength")
                alias = item.get("InterfaceAlias")
                
                # Calculate network (reuse logic or simple string manipulation if needed)
                # For Windows, we might not need the exact network address calculation if we just trust the prefix
                # But to be consistent, let's calculate.
                import struct
                host_bits = 32 - prefix
                netmask = (0xFFFFFFFF >> host_bits) << host_bits
                ip_int = struct.unpack("!I", socket.inet_aton(ip))[0]
                network_int = ip_int & netmask
                network_ip = socket.inet_ntoa(struct.pack("!I", network_int))
                network_cidr = f"{network_ip}/{prefix}"
                
                iface_data = {"name": alias, "ip": ip, "cidr": network_cidr}
                info["interfaces"].append(iface_data)
                
                if ip == info["local_ip"]:
                    info["primary_cidr"] = network_cidr

        except Exception as e:
            logger.error(f"Windows network discovery failed: {e}")
