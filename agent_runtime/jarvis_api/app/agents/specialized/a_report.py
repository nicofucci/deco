"""
A-REPORT: Reporting Agent
Responsible for generating technical and executive reports
"""

import os
from datetime import datetime
from typing import Dict, List, Any
from app.agents.base import BaseAgent
from app.agents.protocol import AgentMessage, AgentResponse, ResponseStatus

class ReportAgent(BaseAgent):
    agent_id = "report-001"
    code = "A-REPORT"
    name = "Reporting Agent"
    version = "1.0.0"
    description = "Generates comprehensive reports from agent data"
    
    @property
    def responsibilities(self) -> List[str]:
        return [
            "Report generation (Markdown, PDF)",
            "Data aggregation",
            "Executive summaries",
            "Technical details formatting"
        ]
    
    @property
    def tools(self) -> List[str]:
        return ["jinja2", "pandoc", "matplotlib"]
    
    @property
    def permissions(self) -> List[str]:
        return ["write_files", "read_all_data"]
    
    async def execute(self, message: AgentMessage) -> AgentResponse:
        action = message.intent
        params = message.params
        
        if action == "generate_report":
            return await self._generate_report(
                params.get("type", "general"),
                params.get("data", {}),
                params.get("title", "Jarvis Report")
            )
        else:
            return AgentResponse(
                request_id=message.request_id,
                agent_code=self.code,
                status=ResponseStatus.FAILED,
                summary=f"Acción desconocida: {action}",
                errors=[f"Unknown action: {action}"]
            )
    
    async def _generate_report(self, report_type: str, data: Dict, title: str) -> AgentResponse:
        """Generate a report file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"report_{report_type}_{timestamp}.md"
        filepath = f"/opt/deco/agent_runtime/logs/reports/{filename}"
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Generate content (Mock for now)
        content = f"""# {title}
**Fecha:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Tipo:** {report_type.upper()}

## Resumen Ejecutivo
Este es un reporte generado automáticamente por Jarvis 3.0.

## Detalles
{str(data)}

## Conclusiones
Se recomienda revisar los hallazgos críticos inmediatamente.
"""
        
        with open(filepath, "w") as f:
            f.write(content)
            
        return AgentResponse(
            request_id="gen-report",
            agent_code=self.code,
            status=ResponseStatus.SUCCESS,
            summary=f"Reporte generado exitosamente: {filename}",
            details={
                "filepath": filepath,
                "format": "markdown",
                "size_bytes": len(content)
            },
            artifacts=[filepath]
        )
