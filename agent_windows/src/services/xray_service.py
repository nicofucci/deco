import logging
import socket
import struct
import platform
import subprocess
import concurrent.futures
import ipaddress
from typing import List, Dict, Any

logger = logging.getLogger("DecoXRay")

class XRayScanner:
    def __init__(self):
        self.os_type = platform.system()

    def get_local_network_info(self):
        """
        Intenta determinar la IP local y la subred.
        """
        try:
            # Hack simple para obtener la IP con rutable
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            
            # Asumimos /24 para simplificar si no podemos obtener mascara real facilmente en python puro multiplatform
            # En producción usaríamos `netifaces` o `psutil`.
            network = ipaddress.IPv4Network(f"{local_ip}/24", strict=False)
            return {
                "ip": local_ip,
                "cidr": str(network),
                "network": network
            }
        except Exception as e:
            logger.error(f"Error detectando red local: {e}")
            return None

    def scan_subnet(self, cidr: str) -> List[Dict[str, Any]]:
        """
        Descubre hosts en la subred usando Ping Sweep y (si es posible) ARP.
        """
        network = ipaddress.IPv4Network(cidr)
        hosts_found = []

        logger.info(f"Iniciando Ping Sweep en {cidr} ({len(list(network.hosts()))} hosts)...")

        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            future_to_ip = {executor.submit(self._ping_host, str(ip)): str(ip) for ip in network.hosts()}
            for future in concurrent.futures.as_completed(future_to_ip):
                ip = future_to_ip[future]
                if future.result():
                    hosts_found.append({"ip": ip})

        logger.info(f"Ping Sweep completado. {len(hosts_found)} hosts activos.")
        return hosts_found

    def resolve_details(self, hosts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Enriquece la lista de hosts con Hostname, MAC, Vendor, OS Guess, Puertos.
        """
        enriched_hosts = []
        for host in hosts:
            ip = host["ip"]
            details = host.copy()
            
            # 1. Hostname (DNS/NetBIOS)
            try:
                hostname, _, _ = socket.gethostbyaddr(ip)
                details["hostname"] = hostname
            except:
                details["hostname"] = "" # No resuelto

            # 2. MAC Address (requiere ARP table lookup local o scapy)
            # Simplificación: En Windows `arp -a` puede funcionar.
            mac = self._get_mac_address(ip)
            if mac:
                details["mac"] = mac
                details["mac_vendor"] = self._lookup_mac_vendor(mac)

            # 3. Port Scan ligero
            open_ports = self._scan_ports(ip, [22, 80, 443, 445, 3389, 9100])
            details["open_ports"] = open_ports
            
            # 4. Device Type & OS Guess
            details["device_type"] = self._guess_device_type(details)
            details["os_guess"] = self._guess_os(details)

            enriched_hosts.append(details)
        
        return enriched_hosts

    def _ping_host(self, ip: str) -> bool:
        param = '-n' if self.os_type.lower() == 'windows' else '-c'
        command = ['ping', param, '1', '-w', '500', ip] # -w 500ms timeout
        if self.os_type.lower() != 'windows':
            command = ['ping', param, '1', '-W', '1', ip] # linux ping timeout is in seconds often
            
        try:
            return subprocess.call(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0
        except:
            return False

    def _get_mac_address(self, ip: str) -> str:
        # Implementación básica parseando arp -a
        try:
            output = subprocess.check_output(f"arp -a {ip}", shell=True).decode()
            # Buscar patrón MAC (XX-XX-XX-XX-XX-XX o XX:XX:...)
            import re
            macs = re.findall(r'([0-9A-Fa-f]{2}[:-][0-9A-Fa-f]{2}[:-][0-9A-Fa-f]{2}[:-][0-9A-Fa-f]{2}[:-][0-9A-Fa-f]{2}[:-][0-9A-Fa-f]{2})', output)
            if macs:
                return macs[0].replace('-', ':').upper()
        except:
            pass
        return None

    def _lookup_mac_vendor(self, mac: str) -> str:
        # Placeholder. En producción usaríamos una DB local OUI.
        if not mac: return None
        prefix = mac[:8]
        # Ejemplos hardcoded
        vendors = {
            "00:0C:29": "VMware",
            "00:50:56": "VMware",
            "B8:27:EB": "Raspberry Pi",
            "DC:A6:32": "Raspberry Pi",
        }
        return vendors.get(prefix, "Unknown Vendor")

    def _scan_ports(self, ip: str, ports: List[int]) -> List[int]:
        open_ports = []
        for port in ports:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.5)
                if s.connect_ex((ip, port)) == 0:
                    open_ports.append(port)
                s.close()
            except:
                pass
        return open_ports

    def _guess_device_type(self, details: Dict[str, Any]) -> str:
        ports = details.get("open_ports", [])
        mac_vendor = details.get("mac_vendor", "") or ""
        hostname = details.get("hostname", "").lower()
        
        # Heuristics
        if "printer" in hostname or 9100 in ports or 631 in ports: return "printer"
        if "camera" in hostname or 554 in ports: return "camera"
        if "Apple" in mac_vendor or "iPhone" in hostname: return "mobile" # Simple assumption
        if "Android" in hostname: return "mobile"
        
        if 3389 in ports or 445 in ports: return "pc" # Likely Windows
        if 22 in ports: 
            if "Raspberry" in mac_vendor: return "iot"
            return "server" # Likely Linux/Server
            
        if 80 in ports or 443 in ports:
             if "router" in hostname or "gateway" in hostname: return "router"
             
        return "unknown"

    def _guess_os(self, details: Dict[str, Any]) -> str:
        ports = details.get("open_ports", [])
        mac_vendor = details.get("mac_vendor", "")
        
        if 445 in ports or 139 in ports or 3389 in ports: return "Windows"
        if 22 in ports: return "Linux/Unix"
        if "Apple" in mac_vendor: return "macOS/iOS"
        return "Unknown OS"

import threading
import time

class PassiveARPMonitor(threading.Thread):
    """
    Monitor pasivo que lee la tabla ARP del sistema periódicamente para detectar 
    dispositivos nuevos sin hacer escaneo activo ruidoso.
    """
    def __init__(self, callback_found_devices):
        super().__init__(daemon=True)
        self.callback = callback_found_devices
        self.known_macs = set()
        self.running = True

    def run(self):
        logger.info("[PassiveARPMonitor] Started.")
        while self.running:
            try:
                current_devices = self._get_arp_table()
                new_devices = []
                for dev in current_devices:
                    if dev['mac'] not in self.known_macs:
                        self.known_macs.add(dev['mac'])
                        new_devices.append(dev)
                
                if new_devices:
                    logger.info(f"[PassiveARPMonitor] Found {len(new_devices)} new devices in ARP cache.")
                    self.callback(new_devices) # Notifica al JobService o XRayService
                    
            except Exception as e:
                logger.error(f"[PassiveARPMonitor] Error: {e}")
            
            time.sleep(30) # Poll every 30s

    def _get_arp_table(self) -> List[Dict[str, str]]:
        devices = []
        try:
            # Cross-platform simple arp -a
            # Windows output: "  192.168.1.1          00-11-22-33-44-55     dynamic"
            output = subprocess.check_output("arp -a", shell=True).decode()
            import re
            # Regex for IP and MAC
            matches = re.findall(r'(\d+\.\d+\.\d+\.\d+)\s+([0-9a-fA-F:-]{17})', output)
            for ip, mac in matches:
                devices.append({"ip": ip, "mac": mac.replace("-", ":").upper()})
        except:
             pass
        return devices

    def stop(self):
        self.running = False
