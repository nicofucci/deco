"""
A-INFRA: Infrastructure & Services Agent
Responsible for maintaining system health and services
"""

import asyncio
import subprocess
from typing import Dict, List, Any
from app.agents.base import BaseAgent
from app.agents.protocol import AgentMessage, AgentResponse, ResponseStatus

class InfraAgent(BaseAgent):
    agent_id = "infra-001"
    code = "A-INFRA"
    name = "Infrastructure Agent"
    version = "1.0.0"
    description = "Monitors and manages system infrastructure and services"
    
    @property
    def responsibilities(self) -> List[str]:
        return [
            "System health checks",
            "Service management (restart, stop, start)",
            "Resource monitoring (CPU, RAM, Disk)",
            "Log retrieval"
        ]
    
    @property
    def tools(self) -> List[str]:
        return ["systemctl", "docker", "ps", "df", "free"]
    
    @property
    def permissions(self) -> List[str]:
        return ["manage_services", "read_logs", "read_metrics"]
    
    async def execute(self, message: AgentMessage) -> AgentResponse:
        action = message.intent
        params = message.params
        
        if action == "health_check":
            return await self._check_health()
        elif action == "restart_service":
            return await self._restart_service(params.get("service_name"))
        elif action == "get_system_status":
            return await self._get_system_status()
        else:
            return AgentResponse(
                request_id=message.request_id,
                agent_code=self.code,
                status=ResponseStatus.FAILED,
                summary=f"Acción desconocida: {action}",
                errors=[f"Unknown action: {action}"]
            )
    
    async def _check_health(self) -> AgentResponse:
        """Check health of critical services"""
        services = ["jarvis-api", "ollama", "postgresql", "minio"]
        status_map = {}
        unhealthy = []
        
        for service in services:
            # Mock check for now, in real env use systemctl is-active
            # status = await self._run_command(f"systemctl is-active {service}")
            status = "active" # Mock
            status_map[service] = status
            if status != "active":
                unhealthy.append(service)
        
        summary = "Todos los sistemas operativos" if not unhealthy else f"Problemas en: {', '.join(unhealthy)}"
        
        return AgentResponse(
            request_id="health-check",
            agent_code=self.code,
            status=ResponseStatus.SUCCESS,
            summary=summary,
            details={"services": status_map}
        )
    
    async def _get_system_status(self) -> AgentResponse:
        """Get system resources status"""
        # Mock metrics
        metrics = {
            "cpu_usage": "15%",
            "ram_usage": "45%",
            "disk_usage": "60%"
        }
        
        return AgentResponse(
            request_id="sys-status",
            agent_code=self.code,
            status=ResponseStatus.SUCCESS,
            summary=f"Sistema estable. CPU: {metrics['cpu_usage']}, RAM: {metrics['ram_usage']}",
            details=metrics
        )
    
    async def _restart_service(self, service_name: str) -> AgentResponse:
        if not service_name:
            return AgentResponse(
                request_id="restart",
                agent_code=self.code,
                status=ResponseStatus.FAILED,
                summary="Nombre de servicio requerido",
                errors=["Missing service_name"]
            )
            
        # await self._run_command(f"systemctl restart {service_name}")
        
        return AgentResponse(
            request_id="restart",
            agent_code=self.code,
            status=ResponseStatus.SUCCESS,
            summary=f"Servicio {service_name} reiniciado correctamente",
            details={"service": service_name, "action": "restart"}
        )
