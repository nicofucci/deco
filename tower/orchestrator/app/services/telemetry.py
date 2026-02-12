
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
from app.models.domain import AgentStatus, Agent, FleetAlert, AgentVersion

# Thresholds
OFFLINE_WARNING_MINUTES = 15
OFFLINE_CRITICAL_HOURS = 1

class AgentTelemetryProcessor:
    def __init__(self, db: Session):
        self.db = db

    def update_agent_status(self, agent_id: str, payload: dict):
        """
        Process heartbeat payload and update AgentStatus.
        """
        # Get or Create Status Record
        status_record = self.db.query(AgentStatus).filter(AgentStatus.agent_id == agent_id).first()
        
        agent = self.db.query(Agent).filter(Agent.id == agent_id).first()
        if not agent:
            return # Should not happen if called from authenticated heartbeat

        if not status_record:
            status_record = AgentStatus(
                agent_id=agent_id,
                client_id=agent.client_id
            )
            self.db.add(status_record)
        
        # Update Fields
        status_record.hostname = payload.get("hostname", agent.hostname)
        status_record.ip = payload.get("ip", agent.ip)
        status_record.version = payload.get("version")
        
        status_record.cpu_usage = payload.get("cpu") or payload.get("load_avg")
        status_record.ram_usage = payload.get("ram") or payload.get("memory_usage")
        
        status_record.last_seen = datetime.now(timezone.utc)
        if payload.get("update_status"):
            status_record.last_update_status = payload.get("update_status")
            status_record.last_update_check = datetime.now(timezone.utc)
            # Reutilizamos error_reason para guardar detalle de target/error
            target = payload.get("update_target_version")
            error = payload.get("update_error")
            reason_parts = []
            if target:
                reason_parts.append(f"target={target}")
            if error:
                reason_parts.append(f"error={error}")
            status_record.error_reason = "; ".join(reason_parts) if reason_parts else status_record.error_reason
        
        # Determine Health State
        status_record.health_state = "healthy"
        
        # Check Version Health
        if status_record.version:
             # Logic to compare with stable version from AgentVersion table
             # optimizing: query stable version only once? 
             # For now, simple check if we have AgentVersion data
             pass 

        # Check Resources (Simple Logic)
        if status_record.cpu_usage and status_record.cpu_usage > 90:
             status_record.health_state = "warning"
             status_record.error_reason = "High CPU Usage"
        
        self.db.commit()
    
    def check_fleet_health(self):
        """
        Periodic worker task: Checks for offline agents.
        """
        now = datetime.now(timezone.utc)
        warning_threshold = now - timedelta(minutes=OFFLINE_WARNING_MINUTES)
        critical_threshold = now - timedelta(hours=OFFLINE_CRITICAL_HOURS)
        
        # Get all statuses
        statuses = self.db.query(AgentStatus).all()
        
        for status in statuses:
            if not status.last_seen:
                continue
                
            if status.last_seen < critical_threshold:
                if status.health_state != "critical":
                    status.health_state = "critical"
                    status.error_reason = "Agent Offline (>1h)"
                    self._create_alert(status, "agent_offline", "critical", "Agent is offline for more than 1 hour")
            
            elif status.last_seen < warning_threshold:
                if status.health_state != "warning" and status.health_state != "critical":
                     status.health_state = "warning"
                     status.error_reason = "Agent Unresponsive (>15m)"
        
        self.db.commit()

    def _create_alert(self, status_record, alert_type, severity, message):
        # Check if active alert exists
        existing = self.db.query(FleetAlert).filter(
            FleetAlert.agent_id == status_record.agent_id,
            FleetAlert.alert_type == alert_type,
            FleetAlert.resolved == False
        ).first()
        
        if existing:
            return # Already alerted
            
        alert = FleetAlert(
            agent_id=status_record.agent_id,
            client_id=status_record.client_id,
            alert_type=alert_type,
            severity=severity,
            message=message
        )
        self.db.add(alert)
