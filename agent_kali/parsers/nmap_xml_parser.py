import xml.etree.ElementTree as ET
from typing import Dict, Any, List

class NmapXMLParser:
    def parse(self, xml_content: str) -> Dict[str, Any]:
        """
        Parsea el output XML de Nmap y devuelve un diccionario estructurado
        compatible con el formato esperado por el Orchestrator.
        """
        try:
            root = ET.fromstring(xml_content)
        except ET.ParseError as e:
            print(f"Error parsing XML: {e}")
            return {}

        result = {
            "tool": "nmap",
            "scan_info": {},
            "hosts": []
        }

        # Scan Info
        scaninfo = root.find("scaninfo")
        if scaninfo is not None:
            result["scan_info"] = scaninfo.attrib

        # Hosts
        for host in root.findall("host"):
            host_data = self._parse_host(host)
            if host_data:
                result["hosts"].append(host_data)
                
        # Simplificación para el parser del Orchestrator (Fase 5)
        # El parser actual espera 'open_ports' en el root o 'ports'
        # Vamos a extraer los puertos del primer host para compatibilidad directa
        if result["hosts"]:
            first_host = result["hosts"][0]
            result["target"] = first_host.get("ip")
            result["hostname"] = first_host.get("hostname")
            result["open_ports"] = [p["port"] for p in first_host.get("ports", [])]
            
        return result

    def _parse_host(self, host: ET.Element) -> Dict[str, Any]:
        status = host.find("status")
        if status is None or status.get("state") != "up":
            return None

        address = host.find("address")
        ip = address.get("addr") if address is not None else None
        
        hostnames = host.find("hostnames")
        hostname = None
        if hostnames is not None:
            hn = hostnames.find("hostname")
            if hn is not None:
                hostname = hn.get("name")

        ports = []
        ports_elem = host.find("ports")
        if ports_elem is not None:
            for port in ports_elem.findall("port"):
                state = port.find("state")
                if state is not None and state.get("state") == "open":
                    port_id = int(port.get("portid"))
                    service = port.find("service")
                    service_name = service.get("name") if service is not None else "unknown"
                    product = service.get("product") if service is not None else None
                    version = service.get("version") if service is not None else None
                    
                    ports.append({
                        "port": port_id,
                        "protocol": port.get("protocol"),
                        "service": service_name,
                        "product": product,
                        "version": version
                    })

        return {
            "ip": ip,
            "hostname": hostname,
            "ports": ports
        }
