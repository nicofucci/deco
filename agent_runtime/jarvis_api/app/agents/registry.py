"""
Agent Registry
Central registry of all available agents
"""

import logging
from typing import Dict, List, Optional, Type
from .base import BaseAgent
from .protocol import AgentStatus

logger = logging.getLogger(__name__)


class AgentRegistry:
    """Central registry for all agents in the system"""
    
    _instance = None
    _agents: Dict[str, BaseAgent] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def register(self, agent: BaseAgent):
        """Register an agent"""
        if agent.code in self._agents:
            logger.warning(f"Agent {agent.code} already registered, overwriting")
        
        self._agents[agent.code] = agent
        logger.info(f"[Registry] Registered agent: {agent.code} - {agent.name}")
    
    def unregister(self, agent_code: str):
        """Unregister an agent"""
        if agent_code in self._agents:
            del self._agents[agent_code]
            logger.info(f"[Registry] Unregistered agent: {agent_code}")
    
    def get(self, agent_code: str) -> Optional[BaseAgent]:
        """Get an agent by code"""
        return self._agents.get(agent_code)
    
    def list_agents(self) -> List[str]:
        """List all registered agent codes"""
        return list(self._agents.keys())
    
    def get_all_info(self) -> List[Dict]:
        """Get information about all agents"""
        return [agent.get_info() for agent in self._agents.values()]
    
    def get_agents_by_status(self, status: AgentStatus) -> List[BaseAgent]:
        """Get agents with specific status"""
        return [
            agent for agent in self._agents.values()
            if agent.status == status
        ]
    
    def get_agents_by_capability(self, capability: str) -> List[BaseAgent]:
        """Get agents that have a specific capability/tool"""
        matching_agents = []
        for agent in self._agents.values():
            if capability.lower() in [t.lower() for t in agent.tools]:
                matching_agents.append(agent)
        return matching_agents
    
    def health_check_all(self) -> Dict[str, Dict]:
        """Health check for all agents"""
        results = {}
        for code, agent in self._agents.items():
            try:
                results[code] = {
                    "status": agent.status.value,
                    "healthy": agent.status != AgentStatus.ERROR,
                    "last_execution": agent.last_execution.isoformat() if agent.last_execution else None
                }
            except Exception as e:
                results[code] = {
                    "status": "error",
                    "healthy": False,
                    "error": str(e)
                }
        
        return results
    
    def __len__(self):
        return len(self._agents)
    
    def __contains__(self, agent_code: str):
        return agent_code in self._agents


# Global registry instance
registry = AgentRegistry()

# Register specialized agents
from .specialized.a_infra import InfraAgent
from .specialized.a_scan import ScanAgent
from .specialized.a_vuln import VulnAgent
from .specialized.a_report import ReportAgent

registry.register(InfraAgent())
registry.register(ScanAgent())
registry.register(VulnAgent())
registry.register(ReportAgent())

# Sprint 3 Agents
from .specialized.a_lab import LabAgent
from .specialized.a_pentest import PentestAgent
from .specialized.a_defense import DefenseAgent
from .specialized.a_guard import GuardAgent

registry.register(LabAgent())
registry.register(PentestAgent())
registry.register(DefenseAgent())
registry.register(GuardAgent())

# Sprint 4 Agents
from .specialized.a_rag import RagAgent
from .specialized.a_compliance import ComplianceAgent

registry.register(RagAgent())
registry.register(ComplianceAgent())

# Sprint 5 Agents
from .specialized.a_ops import OpsAgent
from .specialized.a_ux import UXAgent
from .specialized.a_business import BusinessAgent

registry.register(OpsAgent())
registry.register(UXAgent())
registry.register(BusinessAgent())

# Phase 3 Agents
from .specialized.a_web import WebAgent
from .specialized.a_rag import RagAgent

registry.register(WebAgent())
registry.register(RagAgent())

