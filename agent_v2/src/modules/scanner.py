import psutil
import socket
import logging
from ..core.logger import logger

def scan_local_ports():
    """
    Scans for local open ports (LISTEN) using system APIs.
    Returns list of dicts: {proto, port, pid, name}
    """
    results = []
    try:
        # Get network connections
        connections = psutil.net_connections(kind='inet')
        
        for conn in connections:
            if conn.status == psutil.CONN_LISTEN:
                try:
                    process = psutil.Process(conn.pid)
                    proc_name = process.name()
                except (psutil.NoSuchProcess, psutil.AccessDenied, AttributeError):
                    proc_name = "unknown"

                proto = "tcp" if conn.type == socket.SOCK_STREAM else "udp"
                
                results.append({
                    "protocol": proto,
                    "local_address": f"{conn.laddr.ip}:{conn.laddr.port}",
                    "port": conn.laddr.port,
                    "pid": conn.pid,
                    "process_name": proc_name,
                    "status": conn.status
                })
        
        # Sort by port
        results.sort(key=lambda x: x["port"])
        return results

    except Exception as e:
        logger.error(f"Error during local port scan: {e}")
        return []
