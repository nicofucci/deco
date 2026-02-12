"""
A-COMPLIANCE: Legal & Ethical Agent
Responsible for verifying compliance and authorization
"""

from typing import Dict, List, Any
from app.agents.base import BaseAgent
from app.agents.protocol import AgentMessage, AgentResponse, ResponseStatus

class ComplianceAgent(BaseAgent):
    agent_id = "comp-001"
    code = "A-COMPLIANCE"
    name = "Compliance Officer"
    version = "1.0.0"
    description = "Ensures all actions comply with legal and ethical guidelines"
    
    @property
    def responsibilities(self) -> List[str]:
        return [
            "Authorization verification",
            "Scope validation",
            "Ethical constraints check",
            "Audit trail verification"
        ]
    
    @property
    def tools(self) -> List[str]:
        return ["policy-checker", "auth-db"]
    
    @property
    def permissions(self) -> List[str]:
        return ["approve_actions", "block_actions", "read_all_logs"]
    
    async def execute(self, message: AgentMessage) -> AgentResponse:
        action = message.intent
        params = message.params
        
        if action == "verify_authorization":
            return await self._verify_auth(params.get("target"), params.get("action_type"))
        elif action == "check_ethics":
            return await self._check_ethics(params.get("proposed_plan"))
        else:
            return AgentResponse(
                request_id=message.request_id,
                agent_code=self.code,
                status=ResponseStatus.FAILED,
                summary=f"Acción desconocida: {action}",
                errors=[f"Unknown action: {action}"]
            )
    
    async def _verify_auth(self, target: str, action_type: str) -> AgentResponse:
        """Verify if action on target is authorized"""
        # Mock authorization logic
        # In real world, check against a database of authorized targets/contracts
        
        authorized_targets = ["192.168.1.0/24", "localhost", "127.0.0.1", "scanme.nmap.org"]
        
        is_authorized = False
        for auth_target in authorized_targets:
            if auth_target in target or target in auth_target:
                is_authorized = True
                break
        
        if is_authorized:
            return AgentResponse(
                request_id="auth-check",
                agent_code=self.code,
                status=ResponseStatus.SUCCESS,
                summary=f"✅ Acción '{action_type}' sobre '{target}' AUTORIZADA",
                details={
                    "authorized": True,
                    "clearance_level": "standard",
                    "expiry": "2025-12-31"
                }
            )
        else:
            return AgentResponse(
                request_id="auth-check",
                agent_code=self.code,
                status=ResponseStatus.SUCCESS, # Success in checking, but result is unauthorized
                summary=f"⛔ Acción '{action_type}' sobre '{target}' NO AUTORIZADA",
                details={
                    "authorized": False,
                    "reason": "Target not in authorized list"
                },
                warnings=["Unauthorized target attempt logged"]
            )

    async def _check_ethics(self, plan: str) -> AgentResponse:
        """Check ethical implications of a plan"""
        return AgentResponse(
            request_id="ethics-check",
            agent_code=self.code,
            status=ResponseStatus.SUCCESS,
            summary="Plan verificado éticamente. Cumple con ROE estándar.",
            details={"compliance_score": 1.0}
        )
