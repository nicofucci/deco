from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class AgentDefinition(BaseModel):
    key: str
    name: str
    description: str
    type: str
    test_payload: Dict[str, Any]
    endpoint: Optional[str] = None

def get_all_agents() -> List[AgentDefinition]:
    """Retorna inventario de agentes disponibles para pruebas."""
    return [
        AgentDefinition(
            key="recon_agent",
            name="Agente de Reconocimiento",
            description="Descubrimiento de activos y puertos.",
            type="recon",
            test_payload={"target": "127.0.0.1", "ports": "80,443", "aggressive": False},
            endpoint="/api/agents/recon"
        ),
        AgentDefinition(
            key="vuln_scanner",
            name="Escáner de Vulnerabilidades",
            description="Detección de vulnerabilidades conocidas.",
            type="vuln_scan",
            test_payload={"target": "127.0.0.1", "options": {"mode": "fast"}},
            endpoint="/api/agents/vulnscan"
        ),
        AgentDefinition(
            key="risk_scorer",
            name="Analista de Riesgos",
            description="Calcula score de riesgo basado en hallazgos.",
            type="risk_analysis",
            test_payload={
                "vulns": [
                    {"severity": "High", "cvss": 8.5},
                    {"severity": "Medium", "cvss": 5.0}
                ]
            },
            endpoint=None # Internal only
        ),
        AgentDefinition(
            key="technical_analyst",
            name="Analista Técnico (RAG)",
            description="Genera reportes técnicos usando IA.",
            type="reporting",
            test_payload={"query": "Resumen de estado de seguridad"},
            endpoint="/api/rag/query"
        )
    ]

def get_agent_by_key(key: str) -> Optional[AgentDefinition]:
    """Busca agente por key."""
    for agent in get_all_agents():
        if agent.key == key:
            return agent
    return None
