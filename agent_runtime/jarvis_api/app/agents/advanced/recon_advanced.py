"""
Agente de Reconocimiento Avanzado
Descubrimiento de objetivos con múltiples herramientas
"""

from typing import Dict, List, Any, Optional
import subprocess
import json
from datetime import datetime

class ReconAgentAdvanced:
    """Agente de reconocimiento multi-herramienta."""
    
    def __init__(self, ssh_client=None):
        self.ssh_client = ssh_client
        self.results = {}
    
    async def run_full_discovery(
        self,
        target: str,
        options: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Ejecuta descubrimiento completo de un objetivo.
        
        Args:
            target: IP o dominio objetivo
            options: Opciones de escaneo
                - ports: Puertos a escanear (default: top 1000)
                - aggressive: Modo agresivo (más ruidoso)
                - os_detection: Detectar OS
                - service_version: Detectar versiones
        
        Returns:
            Diccionario con resultados completos
        """
        options = options or {}
        
        results = {
            "target": target,
            "timestamp": datetime.now().isoformat(),
            "phases": {}
        }
        
        # Fase 1: Port Discovery
        results["phases"]["port_scan"] = await self._port_discovery(target, options)
        
        # Fase 2: Service Detection
        if results["phases"]["port_scan"].get("open_ports"):
            results["phases"]["services"] = await self._service_detection(
                target,
                results["phases"]["port_scan"]["open_ports"]
            )
        
        # Fase 3: OS Detection (opcional)
        if options.get("os_detection", False):
            results["phases"]["os"] = await self._os_detection(target)
        
        # Fase 4: Banner Grabbing
        results["phases"]["banners"] = await self._banner_grabbing(
            target,
            results["phases"]["port_scan"].get("open_ports", [])
        )
        
        return results
    
    async def _port_discovery(
        self,
        target: str,
        options: Dict
    ) -> Dict[str, Any]:
        """Descubrimiento de puertos con Nmap."""
        ports = options.get("ports", "1-1000")
        
        # Comando nmap básico
        cmd = [
            "nmap",
            "-p", str(ports),
            "--open",
            "-T4",
            "-oX", "-",  # Output XML
            target
        ]
        
        if options.get("aggressive"):
            cmd.insert(1, "-A")
        
        try:
            # Ejecutar en Kali VM vía SSH si disponible
            if self.ssh_client:
                result = await self._execute_remote(cmd)
            else:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=300
                )
            
            # Parsear resultados
            return self._parse_nmap_output(result.stdout)
        
        except subprocess.TimeoutExpired:
            return {"error": "Timeout en escaneo de puertos"}
        except Exception as e:
            return {"error": str(e)}
    
    async def _service_detection(
        self,
        target: str,
        ports: List[int]
    ) -> Dict[str, Any]:
        """Detección de servicios en puertos abiertos."""
        services = {}
        
        for port in ports[:10]:  # Limitar a 10 puertos
            cmd = [
                "nmap",
                "-p", str(port),
                "-sV",  # Version detection
                "--script=banner",
                target
            ]
            
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                services[str(port)] = self._parse_service_info(result.stdout)
            
            except Exception as e:
                services[str(port)] = {"error": str(e)}
        
        return services
    
    async def _os_detection(self, target: str) -> Dict[str, Any]:
        """Detección de sistema operativo."""
        cmd = ["nmap", "-O", target]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            return self._parse_os_info(result.stdout)
        
        except Exception as e:
            return {"error": str(e)}
    
    async def _banner_grabbing(
        self,
        target: str,
        ports: List[int]
    ) -> Dict[str, str]:
        """Banner grabbing de servicios."""
        banners = {}
        
        for port in ports[:5]:  # Top 5 puertos
            try:
                # Usar netcat para banner grabbing
                cmd = ["nc", "-v", "-w", "3", target, str(port)]
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                banner = result.stdout + result.stderr
                if banner.strip():
                    banners[str(port)] = banner.strip()
            
            except:
                continue
        
        return banners
    
    async def dns_enumeration(self, domain: str) -> Dict[str, Any]:
        """Enumeración DNS de un dominio."""
        results = {
            "domain": domain,
            "records": {}
        }
        
        # Record types a consultar
        record_types = ["A", "AAAA", "MX", "NS", "TXT", "SOA"]
        
        for rtype in record_types:
            try:
                cmd = ["dig", "+short", domain, rtype]
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.stdout.strip():
                    results["records"][rtype] = result.stdout.strip().split("\n")
            
            except:
                continue
        
        return results
    
    async def subdomain_discovery(
        self,
        domain: str,
        wordlist: Optional[str] = None
    ) -> List[str]:
        """Descubrimiento de subdominios."""
        # Wordlist básica
        common_subdomains = [
            "www", "mail", "ftp", "admin", "test", "dev",
            "staging", "api", "app", "portal", "vpn"
        ]
        
        found_subdomains = []
        
        for subdomain in common_subdomains:
            full_domain = f"{subdomain}.{domain}"
            
            try:
                cmd = ["dig", "+short", full_domain, "A"]
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.stdout.strip():
                    found_subdomains.append(full_domain)
            
            except:
                continue
        
        return found_subdomains
    
    def _parse_nmap_output(self, output: str) -> Dict[str, Any]:
        """Parsea salida de nmap."""
        # Parseo básico (en producción usar python-nmap)
        open_ports = []
        
        for line in output.split("\n"):
            if "/tcp" in line and "open" in line:
                try:
                    port = int(line.split("/")[0])
                    open_ports.append(port)
                except:
                    continue
        
        return {
            "open_ports": open_ports,
            "total_found": len(open_ports)
        }
    
    def _parse_service_info(self, output: str) -> Dict[str, str]:
        """Parsea información de servicio."""
        info = {
            "service": "unknown",
            "version": "unknown"
        }
        
        for line in output.split("\n"):
            if "Service Info:" in line:
                info["service"] = line.split("Service Info:")[1].strip()
            elif "Version:" in line:
                info["version"] = line.split("Version:")[1].strip()
        
        return info
    
    def _parse_os_info(self, output: str) -> Dict[str, str]:
        """Parsea detección de OS."""
        for line in output.split("\n"):
            if "OS:" in line:
                return {"os": line.split("OS:")[1].strip()}
        
        return {"os": "unknown"}
    
    async def _execute_remote(self, cmd: List[str]) -> subprocess.CompletedProcess:
        """Ejecuta comando en VM remota vía SSH."""
        # TODO: Implementar ejecución SSH
        cmd_str = " ".join(cmd)
        # Por ahora ejecutar local
        return subprocess.run(cmd, capture_output=True, text=True)
