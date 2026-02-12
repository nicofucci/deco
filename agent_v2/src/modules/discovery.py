import platform
import socket
import psutil
import logging
from ..core.logger import logger

def get_hostname():
    return socket.gethostname()

def get_primary_ip():
    """Attempts to determine the primary outgoing IP."""
    try:
        # Connect to a public DNS to determine correct local interface
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def get_system_info():
    """Returns basic system information."""
    try:
        info = {
            "hostname": get_hostname(),
            "os": platform.system(),
            "os_release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
        }
        return info
    except Exception as e:
        logger.error(f"Error gathering system info: {e}")
        return {}

def get_network_info():
    """Returns detailed network interface information."""
    interfaces = {}
    try:
        stats = psutil.net_if_stats()
        addrs = psutil.net_if_addrs()

        for nic, nic_stats in stats.items():
            # Filter loopback/down unless needed
            if not nic_stats.isup:
                continue
            
            # Simple filter for virtual interfaces (Hyper-V, VMWare) if needed in future
            # for now, we want truth.

            if nic in addrs:
                nic_data = {
                    "is_up": nic_stats.isup,
                    "speed": nic_stats.speed,
                    "mtu": nic_stats.mtu,
                    "ipv4": [],
                    "mac": None
                }
                
                for addr in addrs[nic]:
                    if addr.family == socket.AF_INET:
                        nic_data["ipv4"].append({
                            "address": addr.address,
                            "netmask": addr.netmask,
                            "broadcast": addr.broadcast
                        })
                    # Windows specific for MAC might vary, psutil usually handles it.
                    # On Linux psutil.AF_LINK, on Windows psutil.AF_LINK doesn't exist in some versions,
                    # but usually it's -1 or similar. We check if address looks like a MAC.
                    elif len(str(addr.address).split(':')) == 6 or len(str(addr.address).split('-')) == 6:
                         nic_data["mac"] = addr.address

                if nic_data["ipv4"]: # Only report interfaces with IP
                    interfaces[nic] = nic_data
                    
    except Exception as e:
        logger.error(f"Error gathering network info: {e}")

    return interfaces
