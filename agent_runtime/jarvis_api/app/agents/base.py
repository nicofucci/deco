"""
Base Agent Class
All specialized agents inherit from this base
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from abc import ABC, abstractmethod
from pathlib import Path

from .protocol import AgentMessage, AgentResponse, AgentStatus, ResponseStatus, AuditEntry

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base class for all Jarvis agents"""
    
    # Metadata (to be overridden by subclasses)
    agent_id: str = "base-agent"
    code: str = "A-BASE"
    name: str = "Base Agent"
    version: str = "1.0.0"
    description: str = "Base agent class"
    
    def __init__(self):
        self.status = AgentStatus.IDLE
        self.last_execution: Optional[datetime] = None
        self.audit_log: List[AuditEntry] = []
        self.logger = logging.getLogger(f"agent.{self.code}")
        
        # Ensure log directory exists
        log_dir = Path(f"/opt/deco/agent_runtime/logs/agents/{self.code}")
        log_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"[{self.code}] Agent initialized")
    
    @property
    @abstractmethod
    def responsibilities(self) -> List[str]:
        """What this agent is responsible for"""
        pass
    
    @property
    @abstractmethod
    def tools(self) -> List[str]:
        """Tools/services this agent can use"""
        pass
    
    @property
    @abstractmethod
    def permissions(self) -> List[str]:
        """What this agent is allowed to do"""
        pass
    
    @property
    def input_schema(self) -> Dict:
        """Expected input format (override if needed)"""
        return {
            "type": "object",
            "properties": {
                "action": {"type": "string"},
                "params": {"type": "object"}
            }
        }
    
    @property
    def output_schema(self) -> Dict:
        """Expected output format (override if needed)"""
        return {
            "type": "object",
            "properties": {
                "status": {"type": "string"},
                "summary": {"type": "string"},
                "details": {"type": "object"}
            }
        }
    
    async def handle_message(self, message: AgentMessage) -> AgentResponse:
        """
        Main entry point for handling messages
        
        This method:
        1. Validates the message
        2. Sets agent status to BUSY
        3. Calls the abstract execute() method
        4. Logs the execution
        5. Returns standardized response
        """
        start_time = datetime.now()
        self.status = AgentStatus.BUSY
        
        try:
            self.logger.info(f"[{self.code}] Handling message: {message.intent}")
            
            # Execute agent-specific logic
            response = await self.execute(message)
            
            # Calculate execution time
            execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
            response.execution_time_ms = execution_time
            
            # Audit log
            audit = AuditEntry(
                agent_code=self.code,
                action=message.intent,
                triggered_by=message.from_agent,
                params=message.params,
                result_status=response.status,
                execution_time_ms=execution_time
            )
            self.audit_log.append(audit)
            self._save_audit_log(audit)
            
            self.last_execution = datetime.now()
            self.status = AgentStatus.IDLE
            
            self.logger.info(f"[{self.code}] Completed in {execution_time}ms")
            
            return response
            
        except Exception as e:
            self.logger.error(f"[{self.code}] Error: {e}")
            self.status = AgentStatus.ERROR
            
            return AgentResponse(
                request_id=message.request_id,
                agent_code=self.code,
                status=ResponseStatus.FAILED,
                summary=f"Error en {self.name}: {str(e)}",
                errors=[str(e)]
            )
    
    @abstractmethod
    async def execute(self, message: AgentMessage) -> AgentResponse:
        """
        Agent-specific execution logic
        Must be implemented by each specialized agent
        """
        pass
    
    async def ping(self) -> AgentResponse:
        """Health check endpoint"""
        return AgentResponse(
            request_id="ping",
            agent_code=self.code,
            status=ResponseStatus.SUCCESS,
            summary=f"{self.name} está activo y funcionando",
            details={
                "status": self.status.value,
                "last_execution": self.last_execution.isoformat() if self.last_execution else None,
                "version": self.version
            }
        )
    
    def _save_audit_log(self, audit: AuditEntry):
        """Save audit entry to log file"""
        try:
            log_file = Path(f"/opt/deco/agent_runtime/logs/agents/{self.code}/{datetime.now().strftime('%Y%m%d')}.log")
            log_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(log_file, "a") as f:
                f.write(audit.json() + "\n")
        except Exception as e:
            self.logger.error(f"Failed to save audit log: {e}")
    
    def get_info(self) -> Dict:
        """Get agent information"""
        return {
            "agent_id": self.agent_id,
            "code": self.code,
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "status": self.status.value,
            "last_execution": self.last_execution.isoformat() if self.last_execution else None,
            "responsibilities": self.responsibilities,
            "tools": self.tools,
            "permissions": self.permissions
        }
