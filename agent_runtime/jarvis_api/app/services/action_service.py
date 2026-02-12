from sqlalchemy.orm import Session
from app.models.actions import ProposedAction
from datetime import datetime
import logging
import subprocess

logger = logging.getLogger(__name__)

# BLACKLIST: Actions that require manual intervention and cannot be auto-executed
CRITICAL_ACTIONS = [
    "restart_core_service",
    "shutdown_system",
    "delete_data",
    "aggressive_scan",
    "firewall_change"
]

class ActionService:
    def __init__(self, db: Session):
        self.db = db

    def propose_action(self, type: str, description: str, risk_level: str, source: str, payload: dict = {}, alert_id: str = None):
        """
        Creates a new proposed action in 'pending' state.
        """
        action = ProposedAction(
            type=type,
            description=description,
            risk_level=risk_level,
            recommended_by=source,
            payload=payload,
            source_alert_id=alert_id,
            status="pending"
        )
        self.db.add(action)
        self.db.commit()
        self.db.refresh(action)
        logger.info(f"Action proposed: {type} by {source}")
        return action

    def apply_auto_actions(self, type: str, description: str, risk_level: str, source: str, payload: dict = {}, alert_id: str = None):
        """
        Proposes and potentially executes an action automatically.
        """
        # 1. Propose
        action = self.propose_action(type, description, risk_level, source, payload, alert_id)
        action.status = "auto_proposed"
        self.db.commit()

        # 2. Check Blacklist
        if type in CRITICAL_ACTIONS:
            logger.warning(f"Auto-action {type} is in blacklist. Requiring manual approval.")
            return action # Remains auto_proposed/pending for review

        # 3. Execute if safe
        logger.info(f"Auto-executing safe action: {type}")
        try:
            # Auto-approve
            action.status = "approved"
            self.db.commit()
            # Execute
            self.execute_action(str(action.id), operator="Jarvis AutoDefense")
        except Exception as e:
            logger.error(f"Failed to auto-execute {type}: {e}")
            action.status = "failed"
            self.db.commit()
        
        return action

    def get_pending_actions(self):
        return self.db.query(ProposedAction).filter(ProposedAction.status == "pending").order_by(ProposedAction.created_at.desc()).all()

    def get_action(self, action_id: str):
        return self.db.query(ProposedAction).filter(ProposedAction.id == action_id).first()

    def approve_action(self, action_id: str, operator: str):
        action = self.get_action(action_id)
        if not action:
            return None
        
        if action.status != "pending" and action.status != "auto_proposed":
            raise ValueError(f"Action is {action.status}, cannot approve.")
            
        action.status = "approved"
        action.updated_at = datetime.now()
        self.db.commit()
        return action

    def reject_action(self, action_id: str, operator: str):
        action = self.get_action(action_id)
        if not action:
            return None
            
        action.status = "rejected"
        action.updated_at = datetime.now()
        self.db.commit()
        return action

    def execute_action(self, action_id: str, operator: str):
        """
        Executes an APPROVED action.
        """
        action = self.get_action(action_id)
        if not action:
            return None
            
        if action.status != "approved":
            raise ValueError(f"Action must be approved before execution. Current status: {action.status}")
            
        logger.info(f"Executing action {action.id}: {action.type}")
        
        try:
            success = self._dispatch_execution(action)
            if success:
                action.status = "executed"
                action.executed_at = datetime.now()
                action.executed_by = operator
                self.db.commit()
                return action
            else:
                raise Exception("Execution failed internally")
        except Exception as e:
            logger.error(f"Execution failed for {action.id}: {e}")
            raise e

    def _dispatch_execution(self, action: ProposedAction) -> bool:
        """
        Actual logic to perform the action.
        """
        if action.type == "restart_service":
            service_name = action.payload.get("service")
            if service_name == "qdrant":
                service_name = "deco-qdrant"
            elif service_name == "ollama":
                service_name = "deco-ollama"
            logger.warning(f"Restarting service {service_name}...")
            try:
                # In production, this might need sudo or specific docker socket access
                subprocess.run(["docker", "restart", service_name], check=True)
                return True
            except subprocess.CalledProcessError as e:
                logger.error(f"Docker restart failed: {e}")
                raise e
            
        elif action.type == "run_scan":
            target = action.payload.get("target")
            logger.warning(f"MOCK: Running scan on {target}...")
            return True
            
        elif action.type == "recalculate_risk":
            logger.warning("MOCK: Recalculating risk...")
            return True
            
        return True
