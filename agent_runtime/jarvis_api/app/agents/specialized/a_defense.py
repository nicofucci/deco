"""
A-DEFENSE: Hardening & Defense Agent
Responsible for remediation plans and defensive measures
"""

from typing import Dict, List, Any
from app.agents.base import BaseAgent
from app.agents.protocol import AgentMessage, AgentResponse, ResponseStatus

class DefenseAgent(BaseAgent):
    agent_id = "defense-001"
    code = "A-DEFENSE"
    name = "Defense Architect"
    version = "1.0.0"
    description = "Generates remediation plans and hardening configurations"
    
    @property
    def responsibilities(self) -> List[str]:
        return [
            "Remediation planning",
            "Hardening configuration generation",
            "Security best practices",
            "Patch management advice"
        ]
    
    @property
    def tools(self) -> List[str]:
        return ["cis-cat", "ansible", "hardening-guides"]
    
    @property
    def permissions(self) -> List[str]:
        return ["read_vuln_data", "generate_configs"]
    
    async def execute(self, message: AgentMessage) -> AgentResponse:
        action = message.intent
        params = message.params
        
        if action == "create_remediation_plan":
            return await self._create_plan(params.get("vulnerabilities", []))
        elif action == "generate_hardening":
            return await self._generate_hardening(params.get("system_type"))
        else:
            return AgentResponse(
                request_id=message.request_id,
                agent_code=self.code,
                status=ResponseStatus.FAILED,
                summary=f"Acción desconocida: {action}",
                errors=[f"Unknown action: {action}"]
            )
    
    async def _create_plan(self, vulns: List[Dict]) -> AgentResponse:
        """Create remediation plan from vulnerabilities"""
        plan = []
        for vuln in vulns:
            plan.append({
                "vuln_id": vuln.get("id"),
                "priority": "HIGH" if vuln.get("severity") == "HIGH" else "MEDIUM",
                "action": "Update package / Apply patch",
                "estimated_time": "30m"
            })
            
        return AgentResponse(
            request_id="remediation-plan",
            agent_code=self.code,
            status=ResponseStatus.SUCCESS,
            summary=f"Plan de remediación generado para {len(vulns)} vulnerabilidades",
            details={"plan": plan},
            artifacts=["remediation_plan.md"]
        )

    async def _generate_hardening(self, system_type: str) -> AgentResponse:
        """Generate hardening config"""
        config = ""
        if system_type == "linux":
            config = """
# Linux Hardening
net.ipv4.conf.all.accept_redirects = 0
net.ipv4.conf.all.secure_redirects = 0
kernel.exec-shield = 1
kernel.randomize_va_space = 2
"""
        return AgentResponse(
            request_id="hardening-gen",
            agent_code=self.code,
            status=ResponseStatus.SUCCESS,
            summary=f"Configuración de hardening generada para {system_type}",
            details={"config_snippet": config}
        )
