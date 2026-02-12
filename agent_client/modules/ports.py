import socket
import logging
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

class PortScanner:
    def __init__(self):
        self.common_ports = [21, 22, 23, 25, 53, 80, 110, 135, 139, 143, 443, 445, 3306, 3389, 5432, 8080]

    def check_port(self, ip, port):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((ip, port))
            sock.close()
            if result == 0:
                return port
        except:
            pass
        return None

    def scan_host(self, ip, ports=None):
        if ports is None:
            ports = self.common_ports
            
        logger.info(f"Scanning ports on {ip}...")
        open_ports = []
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            for port in ports:
                futures.append(executor.submit(self.check_port, ip, port))
                
            for future in futures:
                result = future.result()
                if result:
                    open_ports.append(result)
                    
        return open_ports
