import logging
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)

class DecoSupervisor:
    """
    Deco Supervisor: The internal agent responsible for monitoring the health
    and activity of other agents. It enforces rules to prevent spam alerts.
    """

    # Rules for Inactivity Thresholds (None means no inactivity check)
    AGENT_RULES = {
        "technical_analyst": {"inactivity_threshold": None, "description": "On-demand analyst"},
        "risk_scorer": {"inactivity_threshold": None, "description": "Post-pentest scorer"},
        "recon_agent": {"inactivity_threshold": timedelta(hours=24), "description": "Daily reconnaissance"},
        "vuln_scanner": {"inactivity_threshold": timedelta(hours=24), "description": "Scheduled scanner"},
        "reporting_agent": {"inactivity_threshold": None, "description": "On-demand reporter"},
    }

    # Remediation Rules
    REMEDIATION_RULES = {
        "recon_agent": {
            "auto_action_level": "auto", # Changed to auto as requested
            "action_id": "act_01", # Network Discovery
            "description": "Launch Network Discovery Job"
        },
        "vuln_scanner": {
            "auto_action_level": "manual_only",
            "action_id": "act_03", # Vuln Scan Light
            "description": "Relaunch Vulnerability Scan (Light)"
        },
        "qdrant_service": { # New rule for Qdrant
            "auto_action_level": "semi_auto",
            "action_id": "act_restart_qdrant", # Hypothetical action, will map to restart service
            "description": "Restart Qdrant Service"
        }
    }

    @staticmethod
    def analyze_agent_health(agent_key: str, last_run_time: datetime | None) -> dict:
        """
        Analyzes an agent's health based on its last run time and specific rules.
        Returns a dict with status, severity, and supervisor_analysis.
        """
        rule = DecoSupervisor.AGENT_RULES.get(agent_key)
        remediation_rule = DecoSupervisor.REMEDIATION_RULES.get(agent_key)
        
        # If unknown agent, default to a generous threshold (e.g., 48h) or ignore
        if not rule:
            return {"status": "healthy", "severity": "info", "analysis": None}

        threshold = rule["inactivity_threshold"]
        
        # If no threshold defined, this agent is on-demand and cannot be "inactive"
        if threshold is None:
            return {"status": "healthy", "severity": "info", "analysis": None}

        analysis = None
        status = "healthy"
        severity = "info"

        if not last_run_time:
             status = "unhealthy"
             severity = "low"
             analysis = {
                "cause": "Agent has never executed.",
                "action": "Check if the agent is enabled and scheduled.",
                "impact": "Service provided by this agent is unavailable."
            }
        else:
            # Check inactivity
            now = datetime.now(timezone.utc)
            if last_run_time.tzinfo is None:
                last_run_time = last_run_time.replace(tzinfo=timezone.utc)
                
            time_since_run = now - last_run_time

            if time_since_run > threshold:
                status = "unhealthy"
                severity = "low"
                analysis = {
                    "cause": f"Agent inactive for {str(time_since_run).split('.')[0]} (Threshold: {threshold}).",
                    "action": "Verify cron schedule and worker health.",
                    "impact": "Data may be stale."
                }

        # Attach remediation info if unhealthy
        if status == "unhealthy" and remediation_rule:
            analysis["remediation"] = {
                "available": True,
                "auto_action_level": remediation_rule["auto_action_level"],
                "action_id": remediation_rule["action_id"],
                "description": remediation_rule["description"],
                # Initial auto state
                "auto_status": "pending" if remediation_rule["auto_action_level"] == "auto" else None
            }
        
        return {"status": status, "severity": severity, "analysis": analysis}

    @staticmethod
    async def run_auto_remediation_cycle(db_session):
        """
        Periodic task to find and execute pending auto-remediations.
        """
        from app.models.alerts import SystemAlert
        import copy
        
        logger.info("Running Auto-Remediation Cycle...")
        
        alerts = db_session.query(SystemAlert).filter(SystemAlert.status == "open").all()
        
        for alert in alerts:
            if not alert.alert_metadata:
                continue
                
            # We need to work on a copy to ensure we don't modify the DB object in place
            # until we are ready, and to ensure SQLAlchemy detects the change.
            meta_copy = copy.deepcopy(alert.alert_metadata)
            sup_analysis = meta_copy.get("supervisor_analysis", {})
            remediation = sup_analysis.get("remediation", {})
            
            if remediation.get("auto_action_level") == "auto" and remediation.get("auto_status") == "pending":
                # Check cooldown and attempts
                attempts = remediation.get("auto_attempts_count", 0)
                last_attempt = remediation.get("auto_last_attempt_at")
                
                if attempts >= 2:
                    logger.info(f"Alert {alert.id}: Max auto attempts reached.")
                    remediation["auto_status"] = "failed"
                    remediation["auto_last_message"] = "Max attempts reached (2). Manual intervention required."
                    
                    alert.alert_metadata = meta_copy
                    db_session.commit()
                    continue
                
                if last_attempt:
                    last_dt = datetime.fromisoformat(last_attempt)
                    if (datetime.now() - last_dt).total_seconds() < 900: # 15 min cooldown
                        continue

                # Execute!
                logger.info(f"Auto-remediating Alert {alert.id} (Attempt {attempts + 1})")
                try:
                    # Mark as attempting
                    remediation["auto_attempts_count"] = attempts + 1
                    remediation["auto_last_attempt_at"] = datetime.now().isoformat()
                    
                    # Execute
                    result = await DecoSupervisor.execute_remediation(alert.id, "deco_supervisor", db_session)
                    
                    if result["status"] == "success" or result["status"] == "completed":
                        remediation["auto_status"] = "success"
                        remediation["auto_last_message"] = f"Auto-remediation successful. Job ID: {result.get('execution_id')}"
                    else:
                        remediation["auto_status"] = "failed"
                        remediation["auto_last_message"] = f"Execution failed: {result.get('status')}"
                        
                except Exception as e:
                    logger.error(f"Auto-remediation failed for {alert.id}: {e}")
                    remediation["auto_status"] = "failed"
                    remediation["auto_last_message"] = f"Error: {str(e)}"
                
                # Update DB
                alert.alert_metadata = meta_copy
                db_session.commit()

    @staticmethod
    async def execute_remediation(alert_id: str, user_id: str, db_session) -> dict:
        """
        Executes the remediation action for a given alert.
        """
        from app.models.alerts import SystemAlert
        from app.services.kali_runner import kali_runner
        from app.routes.catalog import MOCK_ACTIONS
        
        alert = db_session.query(SystemAlert).filter(SystemAlert.id == alert_id).first()
        if not alert:
            raise ValueError("Alert not found")
            
        if not alert.alert_metadata or not alert.alert_metadata.get("supervisor_analysis", {}).get("remediation", {}).get("available"):
            raise ValueError("No remediation available for this alert")
            
        remediation_config = alert.alert_metadata["supervisor_analysis"]["remediation"]
        action_id = remediation_config["action_id"]
        
        # Special case for Qdrant restart (mock)
        if action_id == "act_restart_qdrant":
             # Mock restart logic
             import asyncio
             await asyncio.sleep(2)
             return {"status": "success", "execution_id": "mock_restart_qdrant"}

        # Find action definition
        action_def = next((a for a in MOCK_ACTIONS if a.id == action_id), None)
        if not action_def:
            raise ValueError(f"Action definition {action_id} not found")

        # Execute
        # We need a target. Usually alerts have metadata['agent_key'] or similar.
        # For recon/vuln, target is usually the network or asset.
        # If missing, we default to a safe target or fail.
        # For now, let's assume a default target or try to find it in alert metadata.
        target = alert.alert_metadata.get("target", "192.168.1.0/24") # Default fallback
        
        try:
            result = await kali_runner.run_action(
                action_id=action_id,
                script_path=action_def.script_path_kali,
                target=target,
                params={}
            )
            
            # Update Alert Metadata with History
            new_metadata = dict(alert.alert_metadata) # Copy
            if "remediation_history" not in new_metadata:
                new_metadata["remediation_history"] = []
                
            new_metadata["remediation_history"].append({
                "timestamp": datetime.now().isoformat(),
                "user": user_id,
                "action_id": action_id,
                "status": result["status"],
                "execution_id": result["execution_id"]
            })
            
            alert.alert_metadata = new_metadata
            db_session.commit()
            
            return {"status": "success", "execution_id": result["execution_id"]}
            
        except Exception as e:
            logger.error(f"Remediation failed: {e}")
            # Log failure
            new_metadata = dict(alert.alert_metadata)
            if "remediation_history" not in new_metadata:
                new_metadata["remediation_history"] = []
                
            new_metadata["remediation_history"].append({
                "timestamp": datetime.now().isoformat(),
                "user": user_id,
                "action_id": action_id,
                "status": "failed",
                "error": str(e)
            })
            alert.alert_metadata = new_metadata
            db_session.commit()
            raise e

