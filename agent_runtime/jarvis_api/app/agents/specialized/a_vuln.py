"""
A-VULN: Vulnerability Analysis Agent
Responsible for identifying vulnerabilities from scan data
"""

from typing import Dict, List, Any
from app.agents.base import BaseAgent
from app.agents.protocol import AgentMessage, AgentResponse, ResponseStatus

class VulnAgent(BaseAgent):
    agent_id = "vuln-001"
    code = "A-VULN"
    name = "Vulnerability Agent"
    version = "1.0.0"
    description = "Analyzes scan results to identify vulnerabilities and CVEs"
    
    @property
    def responsibilities(self) -> List[str]:
        return [
            "Vulnerability assessment",
            "CVE matching",
            "Risk prioritization",
            "Exploit suggestion"
        ]
    
    @property
    def tools(self) -> List[str]:
        return ["searchsploit", "cve-search", "vulners"]
    
    @property
    def permissions(self) -> List[str]:
        return ["read_scan_data", "query_vuln_db"]
    
    async def execute(self, message: AgentMessage) -> AgentResponse:
        action = message.intent
        params = message.params
        
        if action == "analyze_scan":
            return await self._analyze_scan(params.get("scan_results", {}))
        elif action == "check_cve":
            return await self._check_cve(params.get("cve_id"))
        else:
            return AgentResponse(
                request_id=message.request_id,
                agent_code=self.code,
                status=ResponseStatus.FAILED,
                summary=f"Acción desconocida: {action}",
                errors=[f"Unknown action: {action}"]
            )
    
    async def _analyze_scan(self, scan_results: Dict) -> AgentResponse:
        """Analyze scan results for vulnerabilities"""
        # Mock analysis
        vulns = []
        
        services = scan_results.get("services", {})
        if "80" in str(services) or 80 in services:
            vulns.append({
                "id": "CVE-2023-MOCK-1",
                "severity": "HIGH",
                "description": "SQL Injection in login form",
                "service": "http"
            })
            
        return AgentResponse(
            request_id="vuln-analysis",
            agent_code=self.code,
            status=ResponseStatus.SUCCESS,
            summary=f"Análisis completado. Detectadas {len(vulns)} vulnerabilidades potenciales.",
            details={
                "vulnerabilities": vulns,
                "risk_score": 7.5 if vulns else 0.0
            },
            next_steps=["Generar reporte de hallazgos", "Planificar remediación"]
        )
    
    async def _check_cve(self, cve_id: str) -> AgentResponse:
        return AgentResponse(
            request_id="cve-check",
            agent_code=self.code,
            status=ResponseStatus.SUCCESS,
            summary=f"Información encontrada para {cve_id}",
            details={
                "id": cve_id,
                "cvss": 9.8,
                "description": "Remote Code Execution vulnerability"
            }
        )
