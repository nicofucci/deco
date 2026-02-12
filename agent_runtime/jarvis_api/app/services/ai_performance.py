from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, Integer
from datetime import datetime, timedelta

from app.models.ai_benchmarks import AIAgentBenchmark, AIAgentVersion
from app.services.agents_registry import get_all_agents, get_agent_by_key

class AIPerformanceService:
    def __init__(self, db: Session):
        self.db = db

    def get_performance_summary(self) -> Dict[str, Any]:
        """
        Obtiene un resumen enriquecido del rendimiento de todos los agentes.
        Incluye estado calculado (excellent, ok, warning).
        """
        agents = get_all_agents()
        summary_data = []
        
        total_latency = 0
        total_score = 0
        total_success = 0
        active_agents_count = 0

        for agent in agents:
            # Subquery to get latest 50
            subquery = self.db.query(AIAgentBenchmark).filter(
                AIAgentBenchmark.agent_key == agent.key
            ).order_by(desc(AIAgentBenchmark.created_at)).limit(50).subquery()

            # Aggregate from subquery
            stats = self.db.query(
                func.avg(subquery.c.latency_ms).label("avg_latency"),
                func.avg(subquery.c.score_qualitative).label("avg_score"),
                func.count(subquery.c.id).label("total_runs"),
                func.sum(func.cast(subquery.c.success, Integer)).label("success_count")
            ).first()

            if not stats or stats.total_runs == 0:
                summary_data.append({
                    "agent_key": agent.key,
                    "name": agent.name,
                    "version": "v1.0.0", # Placeholder
                    "avg_latency_ms": 0,
                    "avg_score": 0,
                    "success_rate": 0,
                    "status": "unknown",
                    "total_runs": 0
                })
                continue

            avg_latency = float(stats.avg_latency or 0)
            avg_score = float(stats.avg_score or 0)
            success_rate = float(stats.success_count or 0) / float(stats.total_runs)
            
            # Determinar estado
            status = "ok"
            if success_rate < 0.8 or avg_score < 50:
                status = "warning"
            elif success_rate > 0.95 and avg_score > 90:
                status = "excellent"

            summary_data.append({
                "agent_key": agent.key,
                "name": agent.name,
                "version": "v1.0.0",
                "avg_latency_ms": round(avg_latency, 2),
                "avg_score": round(avg_score, 2),
                "success_rate": round(success_rate, 2),
                "status": status,
                "total_runs": stats.total_runs
            })

            total_latency += avg_latency
            total_score += avg_score
            total_success += success_rate
            active_agents_count += 1

        # Global KPIs
        global_kpis = {
            "active_agents": active_agents_count,
            "global_avg_latency": round(total_latency / active_agents_count, 2) if active_agents_count > 0 else 0,
            "global_avg_score": round(total_score / active_agents_count, 2) if active_agents_count > 0 else 0,
            "global_success_rate": round(total_success / active_agents_count, 2) if active_agents_count > 0 else 0
        }

        return {
            "generated_at": datetime.now().isoformat(),
            "global_kpis": global_kpis,
            "agents": summary_data
        }

    def get_agent_history(self, agent_key: str, limit: int = 50) -> Dict[str, Any]:
        """
        Obtiene el historial de benchmarks para un agente específico.
        """
        agent = get_agent_by_key(agent_key)
        if not agent:
            return {"error": "Agente no encontrado"}

        benchmarks = self.db.query(AIAgentBenchmark).filter(
            AIAgentBenchmark.agent_key == agent_key
        ).order_by(desc(AIAgentBenchmark.created_at)).limit(limit).all()

        history = []
        for b in benchmarks:
            history.append({
                "id": str(b.id),
                "created_at": b.created_at.isoformat(),
                "latency_ms": b.latency_ms,
                "score": b.score_qualitative,
                "success": b.success,
                "notes": b.notes
            })

        # Calcular resumen rápido para la cabecera
        summary = self.get_performance_summary()
        agent_summary = next((a for a in summary["agents"] if a["agent_key"] == agent_key), None)

        return {
            "agent": {
                "key": agent.key,
                "name": agent.name,
                "description": agent.description
            },
            "summary": agent_summary,
            "history": history
        }

    def get_ranking(self) -> List[Dict[str, Any]]:
        """
        Devuelve lista de agentes ordenada por un score compuesto.
        Score compuesto = (Success Rate * 50) + (Score * 0.5) - (Latency * 0.01)
        """
        summary = self.get_performance_summary()
        agents = summary["agents"]

        for agent in agents:
            # Calcular ranking score
            # Normalizar latencia: penalizar si es muy alta, pero con límite
            latency_penalty = min(agent["avg_latency_ms"] * 0.1, 20) 
            
            rank_score = (agent["success_rate"] * 100 * 0.4) + (agent["avg_score"] * 0.4) + (20 - latency_penalty)
            agent["ranking_score"] = round(rank_score, 2)

        # Ordenar desc
        return sorted(agents, key=lambda x: x["ranking_score"], reverse=True)


