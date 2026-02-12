import socket
import subprocess
import platform
import json

def get_network_info():
    info = {
        "local_ip": None,
        "primary_cidr": None,
        "interfaces": []
    }
    
    # 1. Get Local IP (Primary)
    try:
        # Connect to a public DNS to determine the primary interface IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        info["local_ip"] = s.getsockname()[0]
        s.close()
    except Exception as e:
        print(f"Could not determine local IP via socket: {e}")
        # Fallback
        info["local_ip"] = socket.gethostbyname(socket.gethostname())

    # 2. Get Interfaces and CIDR (Linux specific for now, as environment is Linux)
    # In a real agent, we might use psutil or netifaces if installed. 
    # Since I cannot install new packages easily, I will use `ip addr` parsing for Linux
    # and `ipconfig` for Windows (though I am on Linux now).
    
    os_type = platform.system()
    
    if os_type == "Linux":
        try:
            output = subprocess.check_output(["ip", "-j", "addr"], text=True)
            interfaces = json.loads(output)
            
            for iface in interfaces:
                name = iface.get("ifname")
                # Skip loopback
                if name == "lo":
                    continue
                
                for addr_info in iface.get("addr_info", []):
                    if addr_info.get("family") == "inet": # IPv4
                        ip = addr_info.get("local")
                        prefixlen = addr_info.get("prefixlen")
                        cidr = f"{ip}/{prefixlen}"
                        
                        # Calculate network address
                        # Simple calculation for display purposes, or use ipcalc if available
                        # For now, just storing the IP/CIDR notation which is what was requested
                        
                        # Calculate network base (e.g. 192.168.1.0/24)
                        # We can do bitwise operations
                        import struct
                        
                        host_bits = 32 - prefixlen
                        netmask = (0xFFFFFFFF >> host_bits) << host_bits
                        ip_int = struct.unpack("!I", socket.inet_aton(ip))[0]
                        network_int = ip_int & netmask
                        network_ip = socket.inet_ntoa(struct.pack("!I", network_int))
                        network_cidr = f"{network_ip}/{prefixlen}"

                        iface_data = {
                            "name": name,
                            "ip": ip,
                            "cidr": network_cidr
                        }
                        info["interfaces"].append(iface_data)
                        
                        # If this IP matches our primary local_ip, set primary_cidr
                        if ip == info["local_ip"]:
                            info["primary_cidr"] = network_cidr
                            
        except Exception as e:
            print(f"Error parsing ip addr: {e}")

    return info

if __name__ == "__main__":
    print(json.dumps(get_network_info(), indent=2))
