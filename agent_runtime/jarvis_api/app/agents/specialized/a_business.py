"""
A-BUSINESS: Business & Product Agent
Responsible for commercial proposals and service catalog
"""

from typing import Dict, List, Any
from app.agents.base import BaseAgent
from app.agents.protocol import AgentMessage, AgentResponse, ResponseStatus

class BusinessAgent(BaseAgent):
    agent_id = "biz-001"
    code = "A-BUSINESS"
    name = "Business Strategist"
    version = "1.0.0"
    description = "Manages service catalog, pricing, and commercial proposals"
    
    @property
    def responsibilities(self) -> List[str]:
        return [
            "Service Catalog Management",
            "Pricing Strategy",
            "Proposal Generation",
            "Client Needs Analysis"
        ]
    
    @property
    def tools(self) -> List[str]:
        return ["pricing-calculator", "proposal-templates"]
    
    @property
    def permissions(self) -> List[str]:
        return ["read_market_data", "generate_proposals"]
    
    async def execute(self, message: AgentMessage) -> AgentResponse:
        action = message.intent
        params = message.params
        
        if action == "create_proposal":
            return await self._create_proposal(params.get("client"), params.get("services"))
        elif action == "get_catalog":
            return await self._get_catalog()
        else:
            return AgentResponse(
                request_id=message.request_id,
                agent_code=self.code,
                status=ResponseStatus.FAILED,
                summary=f"Acción desconocida: {action}",
                errors=[f"Unknown action: {action}"]
            )
    
    async def _create_proposal(self, client: str, services: List[str]) -> AgentResponse:
        total_price = 1500 * len(services) if services else 0
        return AgentResponse(
            request_id="proposal",
            agent_code=self.code,
            status=ResponseStatus.SUCCESS,
            summary=f"Propuesta comercial generada para {client}",
            details={
                "client": client,
                "services": services,
                "total_price": f"${total_price} USD",
                "timeline": "2 weeks"
            },
            artifacts=["proposal_v1.pdf"]
        )

    async def _get_catalog(self) -> AgentResponse:
        catalog = [
            {"name": "Network Audit", "price": "$1500"},
            {"name": "Web Pentest", "price": "$2500"},
            {"name": "Red Teaming", "price": "$5000"}
        ]
        return AgentResponse(
            request_id="catalog",
            agent_code=self.code,
            status=ResponseStatus.SUCCESS,
            summary="Catálogo de servicios actualizado",
            details={"services": catalog}
        )
