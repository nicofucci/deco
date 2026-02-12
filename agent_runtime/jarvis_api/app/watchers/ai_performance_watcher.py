import asyncio
import logging
from datetime import datetime, timedelta, timezone
from sqlalchemy import select, desc, func
from app.database import SessionLocal
from app.models.ai_benchmarks import AIAgentBenchmark
from app.services.alerts_service import create_alert_from_event, create_or_update_alert

logger = logging.getLogger(__name__)

async def start_ai_performance_watcher():
    """
    Monitor AI Agent Benchmarks for performance degradation.
    Runs every 60 seconds.
    """
    logger.info("Starting AI Performance Watcher...")
    while True:
        try:
            await check_ai_performance()
        except Exception as e:
            logger.error(f"Error in AI Performance Watcher: {e}")
        
        await asyncio.sleep(60)

async def check_ai_performance():
    db = SessionLocal()
    try:
        # 1. Check for High Latency (> 2000ms) in recent benchmarks
        recent_benchmarks = db.query(AIAgentBenchmark).filter(
            AIAgentBenchmark.created_at >= datetime.now(timezone.utc) - timedelta(minutes=5)
        ).all()

        for bench in recent_benchmarks:
            if bench.latency_ms > 2000:
                create_alert_from_event(
                    db,
                    event_type="AI_PERFORMANCE",
                    severity="low", # Downgraded from critical as latency is often transient
                    source="ai_benchmarks",
                    title=f"High Latency Detected: {bench.agent_key}",
                    description=f"Agent {bench.agent_key} latency is {bench.latency_ms}ms (Threshold: 2000ms)",
                    metadata={
                        "agent_key": bench.agent_key,
                        "latency_ms": bench.latency_ms,
                        "benchmark_id": str(bench.id),
                        "supervisor_analysis": {
                            "cause": "High network latency or heavy load on LLM provider.",
                            "action": "Monitor for persistence. No immediate action if sporadic.",
                            "impact": "Slower response times for user."
                        }
                    },
                    agent_key=bench.agent_key,
                    metric_value=bench.latency_ms,
                    threshold=2000
                )

            # Check for Low Score (< 70)
            if bench.score_qualitative is not None and bench.score_qualitative < 70:
                create_alert_from_event(
                    db,
                    event_type="AI_PERFORMANCE",
                    severity="medium", # Downgraded from high
                    source="ai_benchmarks",
                    title=f"Low Quality Score: {bench.agent_key}",
                    description=f"Agent {bench.agent_key} score is {bench.score_qualitative} (Threshold: 70)",
                    metadata={
                        "agent_key": bench.agent_key,
                        "score": bench.score_qualitative,
                        "benchmark_id": str(bench.id),
                        "supervisor_analysis": {
                            "cause": "LLM response quality degradation or complex prompt.",
                            "action": "Review prompt templates and LLM parameters.",
                            "impact": "Suboptimal results for specific tasks."
                        }
                    },
                    agent_key=bench.agent_key,
                    score=bench.score_qualitative,
                    threshold=70
                )

        # 2. Check for Consecutive Failures (3 in a row)
        agents = db.query(AIAgentBenchmark.agent_key).distinct().all()
        for agent in agents:
            agent_key = agent[0]
            last_3 = db.query(AIAgentBenchmark).filter(
                AIAgentBenchmark.agent_key == agent_key
            ).order_by(desc(AIAgentBenchmark.created_at)).limit(3).all()

            if len(last_3) == 3 and all(not b.success for b in last_3):
                create_alert_from_event(
                    db,
                    event_type="AI_PERFORMANCE",
                    severity="high", # Critical reserved for system outages
                    source="ai_benchmarks",
                    title=f"Consecutive Failures: {agent_key}",
                    description=f"Agent {agent_key} failed last 3 benchmarks.",
                    metadata={
                        "agent_key": agent_key, 
                        "failures": 3,
                        "supervisor_analysis": {
                            "cause": "Persistent error in agent logic or dependency failure.",
                            "action": "Check agent logs and external service status.",
                            "impact": "Agent is effectively non-functional."
                        }
                    },
                    agent_key=agent_key
                )

        # 3. Check for Inactivity via DecoSupervisor
        from app.services.deco_supervisor import DecoSupervisor
        
        for agent in agents:
            agent_key = agent[0]
            last_run = db.query(AIAgentBenchmark).filter(
                AIAgentBenchmark.agent_key == agent_key
            ).order_by(desc(AIAgentBenchmark.created_at)).first()
            
            last_run_time = last_run.created_at if last_run else None
            
            health = DecoSupervisor.analyze_agent_health(agent_key, last_run_time)
            
            if health["status"] == "unhealthy":
                 create_or_update_alert(
                    db,
                    event_type="AI_PERFORMANCE",
                    severity=health["severity"],
                    source="deco_supervisor",
                    title=f"Agent Health Issue: {agent_key}",
                    description=health["analysis"]["cause"],
                    metadata={
                        "agent_key": agent_key, 
                        "last_run": str(last_run_time),
                        "supervisor_analysis": health["analysis"]
                    },
                    agent_key=agent_key
                )
            elif health["status"] == "healthy":
                # Auto-Close Logic
                from app.services.alerts_service import get_open_alert_by_source, update_alert_status
                
                existing_alert = get_open_alert_by_source(db, source="deco_supervisor", title=f"Agent Health Issue: {agent_key}")
                
                if existing_alert:
                    logger.info(f"Auto-closing alert {existing_alert.id} for {agent_key} (Healthy)")
                    
                    # Add resolution history
                    meta = dict(existing_alert.alert_metadata or {})
                    history = meta.get("remediation_history", [])
                    history.append({
                        "timestamp": datetime.now().isoformat(),
                        "status": "resolved_by_recovery",
                        "message": "Agent returned to healthy state automatically"
                    })
                    meta["remediation_history"] = history
                    
                    # Also check if it was auto-remediated successfully before
                    remediation = meta.get("supervisor_analysis", {}).get("remediation", {})
                    if remediation.get("auto_status") == "success":
                         history.append({
                            "timestamp": datetime.now().isoformat(),
                            "status": "auto_remediation_confirmed",
                            "message": f"Confirmed resolution by auto-remediation {remediation.get('execution_id')}"
                        })
                    
                    existing_alert.alert_metadata = meta
                    existing_alert.closed_at = datetime.now()
                    update_alert_status(db, existing_alert.id, "closed")

    finally:
        db.close()
