import socket
import logging
import psutil
import ipaddress

logger = logging.getLogger("DecoAgent.Discovery")

class NetworkDiscovery:
    def __init__(self):
        self.blacklist_keywords = [
            "vpn", "tap", "tun", "wireguard", "wg", "nord", 
            "vmware", "virtual", "vbox", "loopback", "docker",
            "tailscale", "virbr"
        ]

    def get_network_info(self):
        info = {
            "local_ip": None,
            "primary_cidr": None,
            "interfaces": []
        }
        
        candidates = []

        try:
            # Get all interfaces
            if_addrs = psutil.net_if_addrs()
            
            for iface_name, addrs in if_addrs.items():
                # Filter by blacklist
                lower_name = iface_name.lower()
                if any(keyword in lower_name for keyword in self.blacklist_keywords):
                    continue
                
                for addr in addrs:
                    # Only IPv4
                    if addr.family == socket.AF_INET:
                        ip = addr.address
                        netmask = addr.netmask
                        
                        # Skip loopback IPs just in case
                        if ip.startswith("127."):
                            continue
                            
                        # Calculate CIDR
                        try:
                            network = ipaddress.IPv4Network(f"{ip}/{netmask}", strict=False)
                            cidr = str(network)
                            
                            iface_data = {
                                "name": iface_name,
                                "ip": ip,
                                "netmask": netmask,
                                "cidr": cidr
                            }
                            info["interfaces"].append(iface_data)
                            candidates.append(iface_data)
                            
                        except Exception as e:
                            logger.warning(f"Error calculating CIDR for {iface_name}: {e}")

            # Select primary IP
            # Priority: 192.168.x.x > 10.x.x.x > 172.16-31.x.x > Others
            best_candidate = None
            
            for candidate in candidates:
                ip_obj = ipaddress.IPv4Address(candidate["ip"])
                
                if not best_candidate:
                    best_candidate = candidate
                    continue
                
                # Logic to upgrade best_candidate
                current_best_ip = ipaddress.IPv4Address(best_candidate["ip"])
                
                # If current best is NOT private but new one IS, take new one
                if not current_best_ip.is_private and ip_obj.is_private:
                    best_candidate = candidate
                    continue
                
                # If both are private, prefer 192.168 over 10. over 172.
                if current_best_ip.is_private and ip_obj.is_private:
                    if str(candidate["ip"]).startswith("192.168.") and not str(best_candidate["ip"]).startswith("192.168."):
                        best_candidate = candidate
                    elif str(candidate["ip"]).startswith("10.") and not str(best_candidate["ip"]).startswith("192.168.") and not str(best_candidate["ip"]).startswith("10."):
                        best_candidate = candidate

            if best_candidate:
                info["local_ip"] = best_candidate["ip"]
                info["primary_cidr"] = best_candidate["cidr"]
            else:
                # Fallback if no candidates found (unlikely if network is up)
                try:
                    # Fallback to socket method
                    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    s.connect(("8.8.8.8", 80))
                    fallback_ip = s.getsockname()[0]
                    s.close()
                    info["local_ip"] = fallback_ip
                    # Try to find CIDR for this fallback IP from psutil data even if filtered? 
                    # Or just leave None. Let's leave None or try to match.
                except:
                    pass

        except Exception as e:
            logger.error(f"Error getting network info: {e}")

        return info
