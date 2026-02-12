import socket
import logging
import psutil
import ipaddress
import subprocess
import platform
import concurrent.futures
import requests
from typing import List, Dict, Any
from .utils import setup_logging

logger = setup_logging("DecoNetwork")

class NetworkService:
    def __init__(self):
        self.blacklist_keywords = [
            "vpn", "tap", "tun", "wireguard", "wg", "nord", 
            "vmware", "virtual", "vbox", "loopback", "docker",
            "tailscale", "virbr", "hyper-v", "vethernet"
        ]

    def get_network_info(self) -> Dict[str, Any]:
        """
        Detecta interfaces reales y selecciona la IP principal usando heurística.
        """
        info = {
            "local_ip": None,
            "primary_cidr": None,
            "interfaces": []
        }
        
        candidates = []

        try:
            if_addrs = psutil.net_if_addrs()
            if_stats = psutil.net_if_stats()
            
            for iface_name, addrs in if_addrs.items():
                lower_name = iface_name.lower()
                
                # 1. Filter by blacklist
                if any(keyword in lower_name for keyword in self.blacklist_keywords):
                    continue
                
                # 2. Check if interface is UP
                if iface_name in if_stats and not if_stats[iface_name].isup:
                    continue

                for addr in addrs:
                    if addr.family == socket.AF_INET:
                        ip = addr.address
                        netmask = addr.netmask
                        
                        # 3. Filter Loopback and APIPA
                        if ip.startswith("127.") or ip.startswith("169.254."):
                            continue
                            
                        try:
                            network = ipaddress.IPv4Network(f"{ip}/{netmask}", strict=False)
                            cidr = str(network)
                            
                            iface_data = {
                                "name": iface_name,
                                "ip": ip,
                                "netmask": netmask,
                                "cidr": cidr,
                                "speed": if_stats[iface_name].speed if iface_name in if_stats else 0
                            }
                            info["interfaces"].append(iface_data)
                            candidates.append(iface_data)
                            
                        except Exception as e:
                            logger.warning(f"Error calculating CIDR for {iface_name}: {e}")

            # Heurística para elegir IP principal
            best_candidate = self._select_best_interface(candidates)

            if best_candidate:
                info["local_ip"] = best_candidate["ip"]
                info["primary_cidr"] = best_candidate["cidr"]
            else:
                # Fallback: Google DNS connect
                info["local_ip"] = self._get_fallback_ip()

        except Exception as e:
            logger.error(f"Error getting network info: {e}")

        return info

    def _select_best_interface(self, candidates):
        if not candidates:
            return None
            
        best = candidates[0]
        for c in candidates[1:]:
            best_ip = ipaddress.IPv4Address(best["ip"])
            curr_ip = ipaddress.IPv4Address(c["ip"])
            
            # Prefer 192.168 > 10. > 172.
            if str(c["ip"]).startswith("192.168.") and not str(best["ip"]).startswith("192.168."):
                best = c
            elif str(c["ip"]).startswith("10.") and not str(best["ip"]).startswith("192.168.") and not str(best["ip"]).startswith("10."):
                best = c
            # Prefer higher speed if IPs are in same class preference
            elif best["speed"] < c["speed"]:
                 # Simple tie-breaker if network classes are "equal" in preference
                 best = c
                 
        return best

    def _get_fallback_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"

    def get_public_ip(self) -> str:
        """
        Obtiene la IP pública del agente usando un servicio externo.
        """
        try:
            response = requests.get("https://api.ipify.org?format=json", timeout=5)
            if response.status_code == 200:
                return response.json().get("ip")
        except Exception as e:
            logger.warning(f"Could not get public IP: {e}")
        return None

    def scan_ports(self, target_ip: str, ports: List[int]) -> List[int]:
        """
        Escanea una lista de puertos en una IP específica.
        """
        open_ports = []
        timeout = 0.5 # Fast scan
        
        for port in ports:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(timeout)
                    result = s.connect_ex((target_ip, port))
                    if result == 0:
                        open_ports.append(port)
            except:
                pass
        return open_ports

    def ping_sweep(self, cidr: str) -> List[str]:
        """
        Realiza un ping sweep en el CIDR dado para encontrar hosts vivos.
        """
        active_hosts = []
        try:
            network = ipaddress.IPv4Network(cidr, strict=False)
            # Limit scan to avoid massive networks hang
            hosts = list(network.hosts())
            if len(hosts) > 256:
                logger.warning(f"Network {cidr} too large, scanning first 256 hosts only.")
                hosts = hosts[:256]

            with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
                future_to_ip = {executor.submit(self._ping_host, str(ip)): str(ip) for ip in hosts}
                for future in concurrent.futures.as_completed(future_to_ip):
                    ip = future_to_ip[future]
                    if future.result():
                        active_hosts.append(ip)
                        
        except Exception as e:
            logger.error(f"Ping sweep error: {e}")
            
        return active_hosts

    def _ping_host(self, ip: str) -> bool:
        """
        Ping a single host. Windows specific.
        """
        try:
            startupinfo = None
            creationflags = 0
            if platform.system() == 'Windows':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
                creationflags = 0x08000000 # CREATE_NO_WINDOW

            # Use subprocess.run with timeout to avoid hanging
            proc = subprocess.run(
                ["ping", "-n", "1", "-w", "500", ip],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                stdin=subprocess.DEVNULL,
                timeout=2, # Python-level timeout
                text=True,
                startupinfo=startupinfo,
                creationflags=creationflags,
                errors='ignore' # Prevent encoding crashes
            )
            
            output = proc.stdout
            return "TTL=" in output or "ttl=" in output
            
        except subprocess.TimeoutExpired:
            return False
        except Exception:
            return False

    def resolve_hostname(self, ip: str) -> str:
        """
        Intenta resolver el hostname de una IP.
        """
        try:
            hostname, _, _ = socket.gethostbyaddr(ip)
            return hostname
        except:
            return None

    def grab_banner(self, ip: str, port: int) -> str:
        """
        Intenta obtener el banner de un servicio.
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1.0)
                s.connect((ip, port))
                # Enviar algo genérico para provocar respuesta
                s.send(b"HEAD / HTTP/1.0\r\n\r\n")
                banner = s.recv(1024).decode('utf-8', errors='ignore').strip()
                return banner
        except:
            return None
