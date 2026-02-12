"""
Agente de Escaneo de Vulnerabilidades
Detección automática de CVEs y vulnerabilidades conocidas
"""

from typing import Dict, List, Any
import re
from datetime import datetime

class VulnScannerAgent:
    """Escáner de vulnerabilidades automatizado."""
    
    def __init__(self, ollama_client=None):
        self.ollama = ollama_client
        self.cve_database = {}  # Caché de CVEs
    
    async def scan_target(
        self,
        target: str,
        services: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Escanea objetivo buscando vulnerabilidades.
        
        Args:
            target: IP/dominio objetivo
            services: Servicios detectados (de ReconAgent)
        
        Returns:
            Lista de vulnerabilidades encontradas
        """
        vulnerabilities = []
        
        # Escanear cada servicio
        for port, service_info in services.items():
            vulns = await self._scan_service(
                target,
                port,
                service_info
            )
            vulnerabilities.extend(vulns)
        
        return vulnerabilities
    
    async def _scan_service(
        self,
        target: str,
        port: str,
        service_info: Dict
    ) -> List[Dict]:
        """Escanea un servicio específico."""
        vulns = []
        
        # Detección basada en versión
        service_name = service_info.get("service", "unknown")
        version = service_info.get("version", "")
        
        if version:
            # Buscar CVEs conocidos para esa versión
            cves = await self._search_cves(service_name, version)
            
            for cve in cves:
                vulns.append({
                    "target": target,
                    "port": port,
                    "service": service_name,
                    "version": version,
                    "cve_id": cve["id"],
                    "severity": cve["severity"],
                    "description": cve["description"],
                    "cvss_score": cve.get("cvss_score", 0),
                    "exploitability": cve.get("exploitability", "unknown")
                })
        
        # Checks adicionales
        vulns.extend(await self._common_misconfigurations(target, port, service_name))
        
        return vulns
    
    async def _search_cves(
        self,
        service: str,
        version: str
    ) -> List[Dict]:
        """Busca CVEs para servicio y versión."""
        # Database estática de CVEs comunes
        # En producción: integrar con NVD API
        
        known_vulns = {
            "apache": {
                "2.4.49": [
                    {
                        "id": "CVE-2021-41773",
                        "severity": "Critical",
                        "cvss_score": 9.8,
                        "description": "Path traversal en Apache 2.4.49",
                        "exploitability": "high"
                    }
                ],
                "2.4.50": [
                    {
                        "id": "CVE-2021-42013",
                        "severity": "Critical",
                        "cvss_score": 9.8,
                        "description": "Path traversal y RCE en Apache 2.4.50",
                        "exploitability": "high"
                    }
                ]
            },
            "openssh": {
                "7.4": [
                    {
                        "id": "CVE-2018-15473",
                        "severity": "Medium",
                        "cvss_score": 5.3,
                        "description": "Username enumeration en OpenSSH <= 7.7",
                        "exploitability": "medium"
                    }
                ]
            },
            "mysql": {
                "5.5": [
                    {
                        "id": "CVE-2016-6662",
                        "severity": "High",
                        "cvss_score": 9.0,
                        "description": "Privilege escalation en MySQL 5.5.x",
                        "exploitability": "medium"
                    }
                ]
            }
        }
        
        service_lower = service.lower()
        
        for service_name, versions in known_vulns.items():
            if service_name in service_lower:
                for vuln_version, cves in versions.items():
                    if vuln_version in version:
                        return cves
        
        return []
    
    async def _common_misconfigurations(
        self,
        target: str,
        port: str,
        service: str
    ) -> List[Dict]:
        """Detecta configuraciones inseguras comunes."""
        misconfigs = []
        
        # FTP anónimo
        if "ftp" in service.lower() and port == "21":
            misconfigs.append({
                "target": target,
                "port": port,
                "service": service,
                "type": "misconfiguration",
                "severity": "Medium",
                "description": "FTP service exposed (possible anonymous access)",
                "recommendation": "Disable anonymous FTP or use SFTP"
            })
        
        # Telnet (inherently insecure)
        if "telnet" in service.lower() and port == "23":
            misconfigs.append({
                "target": target,
                "port": port,
                "service": service,
                "type": "misconfiguration",
                "severity": "High",
                "description": "Telnet service exposed (unencrypted)",
                "recommendation": "Disable Telnet and use SSH instead"
            })
        
        # SMB legacy
        if "smb" in service.lower() and port in ["139", "445"]:
            misconfigs.append({
                "target": target,
                "port": port,
                "service": service,
                "type": "misconfiguration",
                "severity": "Medium",
                "description": "SMB service exposed (check for SMBv1)",
                "recommendation": "Disable SMBv1 and restrict access"
            })
        
        return misconfigs
    
    async def analyze_with_llm(
        self,
        vulnerability: Dict
    ) -> Dict[str, Any]:
        """Analiza vulnerabilidad con LLM para contexto adicional."""
        if not self.ollama:
            return {"analysis": "LLM not available"}
        
        prompt = f"""Analiza esta vulnerabilidad desde perspectiva defensiva:

CVE: {vulnerability.get('cve_id', 'N/A')}
Servicio: {vulnerability.get('service')}
Severidad: {vulnerability.get('severity')}
CVSS: {vulnerability.get('cvss_score')}

Proporciona:
1. Riesgo real en entorno de producción
2. Pasos de mitigación inmediatos
3. Controles compensatorios

Respuesta concisa en 3 puntos."""

        response = self.ollama.chat(
            messages=[{"role": "user", "content": prompt}]
        )
        
        return {
            "llm_analysis": response.get("message", {}).get("content", "")
        }
    
    async def prioritize_vulnerabilities(
        self,
        vulnerabilities: List[Dict]
    ) -> List[Dict]:
        """Prioriza vulnerabilidades por riesgo."""
        # Scoring personalizado
        for vuln in vulnerabilities:
            score = 0
            
            # Base: CVSS score
            score += vuln.get("cvss_score", 0) * 10
            
            # Multiplicador por severidad
            severity = vuln.get("severity", "Low")
            if severity == "Critical":
                score *= 1.5
            elif severity == "High":
                score *= 1.3
            elif severity == "Medium":
                score *= 1.1
            
            # Multiplicador por explotabilidad
            exploit = vuln.get("exploitability", "unknown")
            if exploit == "high":
                score *= 1.4
            elif exploit == "medium":
                score *= 1.2
            
            vuln["priority_score"] = min(score, 100)
        
        # Ordenar por score
        return sorted(
            vulnerabilities,
            key=lambda v: v.get("priority_score", 0),
            reverse=True
        )
