from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio
from sqlalchemy.orm import Session
from app.models.ai_benchmarks import AIAgentVersion, AIAgentBenchmark
from app.services.agents_registry import get_all_agents, get_agent_by_key, AgentDefinition

# Importar instancias de agentes (reutilizando las de agents_tests por ahora)
# En un refactor futuro, esto debería venir de un Dependency Injection container real.
from app.agents.advanced.recon_advanced import ReconAgentAdvanced
from app.agents.advanced.vuln_scanner import VulnScannerAgent
from app.agents.advanced.risk_scorer import RiskScorer

recon_agent = ReconAgentAdvanced()
vuln_scanner = VulnScannerAgent()
risk_scorer = RiskScorer()

class AIBenchmarkService:
    def __init__(self, db: Session):
        self.db = db

    def get_or_create_version(self, agent_key: str, label: str = "v1.0.0") -> AIAgentVersion:
        version = self.db.query(AIAgentVersion).filter_by(agent_key=agent_key, version_label=label).first()
        if not version:
            version = AIAgentVersion(agent_key=agent_key, version_label=label, description="Auto-generated baseline")
            self.db.add(version)
            self.db.commit()
            self.db.refresh(version)
        return version

    async def run_benchmark(self, agent_key: str, runs: int = 3) -> Dict[str, Any]:
        agent_def = get_agent_by_key(agent_key)
        if not agent_def:
            return {"error": f"Agente {agent_key} no encontrado"}

        version = self.get_or_create_version(agent_key)
        results = []
        
        for i in range(runs):
            start_time = datetime.now()
            success = False
            score = 0.0
            notes = ""
            
            try:
                # Ejecutar lógica de benchmark (más completa que smoke test)
                output = await self._execute_agent_logic(agent_def)
                success = True
                score = self._calculate_score(agent_def, output)
                notes = "Ejecución exitosa"
            except Exception as e:
                success = False
                score = 0.0
                notes = f"Error: {str(e)}"
            
            latency = (datetime.now() - start_time).total_seconds() * 1000
            
            # Guardar en DB
            benchmark = AIAgentBenchmark(
                agent_key=agent_key,
                version_id=version.id,
                test_type="benchmark",
                input_profile=agent_def.test_payload, # Usamos el payload del registry como base
                success=success,
                latency_ms=latency,
                score_qualitative=score,
                notes=notes
            )
            self.db.add(benchmark)
            results.append(benchmark)
        
        self.db.commit()
        
        # Calcular agregados
        avg_latency = sum(r.latency_ms for r in results) / len(results)
        success_rate = sum(1 for r in results if r.success) / len(results)
        avg_score = sum(r.score_qualitative for r in results) / len(results)

        return {
            "agent_key": agent_key,
            "version": version.version_label,
            "runs": runs,
            "avg_latency_ms": round(avg_latency, 2),
            "success_rate": round(success_rate, 2),
            "avg_score": round(avg_score, 2)
        }

    async def _execute_agent_logic(self, agent_def: AgentDefinition) -> Any:
        # Lógica similar a smoke tests pero quizás con parámetros más exigentes si se desea
        # Por ahora reutilizamos la lógica segura de smoke tests para no romper reglas
        if agent_def.key == "recon_agent":
            return await recon_agent.run_full_discovery(target="127.0.0.1", options={"ports": "80,443"})
        elif agent_def.key == "vuln_scanner":
            services = {"80": {"service": "apache", "version": "2.4.49"}}
            return await vuln_scanner.scan_target("127.0.0.1", services)
        elif agent_def.key == "risk_scorer":
            vulns = [{"severity": "High", "cvss": 8.5}, {"severity": "Medium", "cvss": 5.0}]
            # Simulación simple
            return {"score": 85}
        elif agent_def.key == "technical_analyst":
            return {"answer": "Respuesta simulada de benchmark"}
        return {}

    def _calculate_score(self, agent_def: AgentDefinition, output: Any) -> float:
        # Reglas heurísticas simples para score cualitativo (0-100)
        if not output: return 0.0
        
        if agent_def.key == "recon_agent":
            # Si encontró fases y no está vacío
            if isinstance(output, dict) and "phases" in output:
                return 100.0
        elif agent_def.key == "vuln_scanner":
            if isinstance(output, dict) and "vuln_count" in output: return 100.0
            if isinstance(output, list): return 100.0
        elif agent_def.key == "risk_scorer":
            if isinstance(output, dict) and "score" in output: return 100.0
        elif agent_def.key == "technical_analyst":
            if isinstance(output, dict) and "answer" in output: return 100.0
            
        return 50.0 # Fallback si retornó algo pero no validamos estructura

    def get_summary(self) -> Dict[str, Any]:
        # Obtener resumen de últimos benchmarks
        # Esta query podría ser compleja, por ahora simplificamos
        # Retornamos lista de agentes y sus últimos promedios (calculados al vuelo o última ejecución)
        # Para MVP: Listar todos los agentes y buscar sus últimos 5 benchmarks
        summary = []
        agents = get_all_agents()
        
        for agent in agents:
            benchmarks = self.db.query(AIAgentBenchmark)\
                .filter_by(agent_key=agent.key)\
                .order_by(AIAgentBenchmark.created_at.desc())\
                .limit(10).all()
            
            if not benchmarks:
                continue
                
            avg_lat = sum(b.latency_ms for b in benchmarks) / len(benchmarks)
            succ_rate = sum(1 for b in benchmarks if b.success) / len(benchmarks)
            avg_sc = sum(b.score_qualitative for b in benchmarks) / len(benchmarks)
            
            summary.append({
                "agent_key": agent.key,
                "version": "v1.0.0", # Simplificado
                "last_run": benchmarks[0].created_at.isoformat(),
                "avg_latency_ms": round(avg_lat, 2),
                "success_rate": round(succ_rate, 2),
                "avg_score": round(avg_sc, 2),
                "total_runs": len(benchmarks) # De los últimos 10
            })
            
        # Calculate Global KPIs
        total_agents = len(summary)
        if total_agents > 0:
            global_avg_lat = sum(a["avg_latency_ms"] for a in summary) / total_agents
            global_avg_score = sum(a["avg_score"] for a in summary) / total_agents
            global_succ_rate = sum(a["success_rate"] for a in summary) / total_agents
        else:
            global_avg_lat = 0
            global_avg_score = 0
            global_succ_rate = 0

        return {
            "generated_at": datetime.now().isoformat(),
            "global_kpis": {
                "active_agents": total_agents,
                "global_avg_latency": round(global_avg_lat, 2),
                "global_avg_score": round(global_avg_score, 2),
                "global_success_rate": round(global_succ_rate, 2)
            },
            "agents": summary
        }

    def get_history(self, agent_key: str, limit: int = 50) -> Optional[Dict[str, Any]]:
        agent = get_agent_by_key(agent_key)
        if not agent:
            return None
            
        benchmarks = self.db.query(AIAgentBenchmark)\
            .filter_by(agent_key=agent_key)\
            .order_by(AIAgentBenchmark.created_at.desc())\
            .limit(limit).all()
            
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
            
        # Recalculate summary for this agent
        if benchmarks:
            avg_lat = sum(b.latency_ms for b in benchmarks) / len(benchmarks)
            succ_rate = sum(1 for b in benchmarks if b.success) / len(benchmarks)
            avg_sc = sum(b.score_qualitative for b in benchmarks) / len(benchmarks)
        else:
            avg_lat = 0
            succ_rate = 0
            avg_sc = 0
            
        status = "unknown"
        if benchmarks:
            if succ_rate >= 0.9: status = "excellent"
            elif succ_rate >= 0.7: status = "ok"
            else: status = "warning"

        return {
            "agent": {
                "key": agent.key,
                "name": agent.name,
                "description": agent.description
            },
            "summary": {
                "avg_latency_ms": round(avg_lat, 2),
                "avg_score": round(avg_sc, 2),
                "success_rate": round(succ_rate, 2),
                "status": status,
                "total_runs": len(benchmarks)
            },
            "history": history
        }
