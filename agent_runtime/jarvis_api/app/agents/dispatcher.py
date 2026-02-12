"""
Agent Dispatcher
Routes requests from Jarvis Prime to appropriate agents
"""

import logging
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime

from .base import BaseAgent
from .registry import registry
from .protocol import AgentMessage, AgentResponse, ResponseStatus

logger = logging.getLogger(__name__)


class DispatchResult:
    """Result of a dispatch operation"""
    
    def __init__(
        self, 
        workflow_id: str = None,
        success: bool = True,
        responses: List[AgentResponse] = None,
        summary: str = "",
        details: Dict = None,
        artifacts: List[str] = None
    ):
        self.workflow_id = workflow_id
        self.responses = responses or []
        self.agents_used = [r.agent_code for r in self.responses]
        self.total_time_ms = sum(r.execution_time_ms or 0 for r in self.responses)
        self.success = success
        self.summary = summary
        self.details = details or {}
        self.artifacts = artifacts or []
    
    def add_response(self, response: AgentResponse):
        """Add an agent response to results"""
        self.responses.append(response)
        self.agents_used.append(response.agent_code)
        self.total_time_ms += response.execution_time_ms or 0
        
        if response.status == ResponseStatus.FAILED:
            self.success = False
        
        self.artifacts.extend(response.artifacts)
    
    def to_dict(self) -> Dict:
        return {
            "workflow_id": self.workflow_id,
            "agents_used": self.agents_used,
            "total_time_ms": self.total_time_ms,
            "success": self.success,
            "summary": self.summary,
            "details": self.details,
            "artifacts": self.artifacts,
            "responses": [r.dict() for r in self.responses]
        }


class AgentDispatcher:
    """Dispatches requests to appropriate agents"""
    
    def __init__(self):
        self.registry = registry
        self.logger = logging.getLogger("dispatcher")
    
    async def dispatch_to_agent(
        self,
        agent_code: str,
        intent: str,
        params: Dict[str, Any],
        context: Dict[str, Any] = None,
        from_agent: str = "jarvis-prime"
    ) -> AgentResponse:
        """
        Dispatch a message to a specific agent
        
        Args:
            agent_code: Target agent code (e.g., "A-SCAN")
            intent: What to do (e.g., "scan_target")
            params: Parameters for the action
            context: Shared context
            from_agent: Who is sending the message
        
        Returns:
            AgentResponse from the target agent
        """
        agent = self.registry.get(agent_code)
        
        if not agent:
            self.logger.error(f"Agent {agent_code} not found in registry")
            return AgentResponse(
                request_id=str(uuid.uuid4()),
                agent_code=agent_code,
                status=ResponseStatus.FAILED,
                summary=f"Agente {agent_code} no encontrado",
                errors=[f"Agent {agent_code} not registered"]
            )
        
        message = AgentMessage(
            request_id=str(uuid.uuid4()),
            from_agent=from_agent,
            to_agent=agent_code,
            intent=intent,
            params=params,
            context=context or {}
        )
        
        self.logger.info(f"[Dispatcher] {from_agent} -> {agent_code}: {intent}")
        
        try:
            response = await agent.handle_message(message)
            return response
        except Exception as e:
            self.logger.error(f"[Dispatcher] Error dispatching to {agent_code}: {e}")
            return AgentResponse(
                request_id=message.request_id,
                agent_code=agent_code,
                status=ResponseStatus.FAILED,
                summary=f"Error al ejecutar {agent_code}: {str(e)}",
                errors=[str(e)]
            )
    
    async def dispatch_to_multiple(
        self,
        agents: List[tuple],  # List of (agent_code, intent, params)
        context: Dict[str, Any] = None,
        parallel: bool = False
    ) -> DispatchResult:
        """
        Dispatch to multiple agents
        
        Args:
            agents: List of (agent_code, intent, params) tuples
            context: Shared context
            parallel: Whether to run in parallel (not implemented yet)
        
        Returns:
            DispatchResult with all responses
        """
        result = DispatchResult()
        shared_context = context or {}
        
        for agent_code, intent, params in agents:
            response = await self.dispatch_to_agent(
                agent_code,
                intent,
                params,
                shared_context
            )
            
            result.add_response(response)
            
            # Share results in context for next agents
            shared_context[f"{agent_code}_result"] = response.dict()
        
        return result
    
    async def execute_workflow(
        self,
        workflow_name: str,
        params: Dict[str, Any]
    ) -> DispatchResult:
        """
        Execute a predefined workflow
        
        Workflows are sequences of agent calls
        """
        from .workflows import get_workflow
        
        workflow = get_workflow(workflow_name)
        
        if not workflow:
            result = DispatchResult()
            result.success = False
            result.summary = f"Workflow '{workflow_name}' no encontrado"
            return result
        
        self.logger.info(f"[Dispatcher] Executing workflow: {workflow_name}")
        
        return await workflow.execute(self, params)
    
    def get_available_agents(self) -> List[Dict]:
        """Get list of all available agents"""
        return self.registry.get_all_info()
    
    async def ping_all_agents(self) -> Dict[str, AgentResponse]:
        """Ping all agents to check health"""
        results = {}
        
        for agent_code in self.registry.list_agents():
            agent = self.registry.get(agent_code)
            if agent:
                try:
                    results[agent_code] = await agent.ping()
                except Exception as e:
                    results[agent_code] = AgentResponse(
                        request_id="ping",
                        agent_code=agent_code,
                        status=ResponseStatus.FAILED,
                        summary=f"Ping failed: {e}",
                        errors=[str(e)]
                    )
        
        return results


# Global dispatcher instance
dispatcher = AgentDispatcher()
