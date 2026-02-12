from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.models.alerts import SystemAlert
from app.schemas.alerts import AlertCreate

def create_alert(db: Session, alert_data: AlertCreate) -> SystemAlert:
    """
    Creates a new system alert.
    """
    # Map Pydantic model to SQLAlchemy model
    # Note: alert_data.metadata is mapped to SystemAlert.alert_metadata
    db_alert = SystemAlert(
        type=alert_data.type,
        severity=alert_data.severity,
        source=alert_data.source,
        title=alert_data.title,
        description=alert_data.description,
        agent_key=alert_data.agent_key,
        client_id=alert_data.client_id,
        asset_id=alert_data.asset_id,
        scan_id=alert_data.scan_id,
        score=alert_data.score,
        metric_value=alert_data.metric_value,
        threshold=alert_data.threshold,
        alert_metadata=alert_data.metadata, # Mapping here
        agent_name=alert_data.agent_name,
        last_heartbeat=alert_data.last_heartbeat,
        recommended_action=alert_data.recommended_action,
        status="open"
    )
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return db_alert

def list_alerts(
    db: Session, 
    status: Optional[str] = None, 
    severity: Optional[str] = None, 
    type: Optional[str] = None, 
    agent_key: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
) -> List[SystemAlert]:
    """
    List alerts with optional filters.
    """
    query = db.query(SystemAlert)
    
    if status:
        query = query.filter(SystemAlert.status == status)
    if severity:
        query = query.filter(SystemAlert.severity == severity)
    if type:
        query = query.filter(SystemAlert.type == type)
    if agent_key:
        query = query.filter(SystemAlert.agent_key == agent_key)
        
    return query.order_by(SystemAlert.created_at.desc()).offset(offset).limit(limit).all()

def get_alert(db: Session, alert_id: str) -> Optional[SystemAlert]:
    """
    Get a specific alert by ID.
    """
    return db.query(SystemAlert).filter(SystemAlert.id == alert_id).first()

def get_open_alert_by_source(db: Session, source: str, title: str = None) -> Optional[SystemAlert]:
    """
    Find an open alert by source and optionally title.
    """
    query = db.query(SystemAlert).filter(
        SystemAlert.source == source,
        SystemAlert.status.in_(["open", "acknowledged"])
    )
    if title:
        query = query.filter(SystemAlert.title == title)
    
    return query.order_by(SystemAlert.created_at.desc()).first()

def update_alert_status(db: Session, alert_id: str, new_status: str) -> Optional[SystemAlert]:
    """
    Update the status of an alert and set timestamps accordingly.
    """
    alert = get_alert(db, alert_id)
    if not alert:
        return None
        
    old_status = alert.status
    alert.status = new_status
    
    now = datetime.now()
    
    if new_status == "acknowledged" and old_status == "open":
        if not alert.acknowledged_at:
            alert.acknowledged_at = now
            
    if new_status == "resolved":
        alert.resolved_at = now
        
    # If moving back to open, we don't clear timestamps, just update status.
    
    db.commit()
    db.refresh(alert)
    return alert

def create_alert_from_event(
    db: Session, 
    *, 
    event_type: str, 
    severity: str, 
    title: str, 
    description: str, 
    **kwargs
) -> SystemAlert:
    """
    Helper to create an alert from an internal event.
    kwargs can include: agent_key, client_id, asset_id, scan_id, score, metric_value, threshold, metadata, source...
    """
    # Construct AlertCreate object or dict
    alert_data = AlertCreate(
        type=event_type,
        severity=severity,
        title=title,
        description=description,
        source=kwargs.get("source", "system_event"),
        agent_key=kwargs.get("agent_key"),
        client_id=kwargs.get("client_id"),
        asset_id=kwargs.get("asset_id"),
        scan_id=kwargs.get("scan_id"),
        score=kwargs.get("score"),
        metric_value=kwargs.get("metric_value"),
        threshold=kwargs.get("threshold"),
        metadata=kwargs.get("metadata"),
        agent_name=kwargs.get("agent_name"),
        last_heartbeat=kwargs.get("last_heartbeat"),
        recommended_action=kwargs.get("recommended_action")
    )
    return create_alert(db, alert_data)

def create_or_update_alert(
    db: Session, 
    *, 
    event_type: str, 
    severity: str, 
    title: str, 
    description: str, 
    **kwargs
) -> SystemAlert:
    """
    Creates a new alert OR updates an existing open alert for the same agent/source.
    Implements "One Active Alert per Agent" rule.
    """
    agent_key = kwargs.get("agent_key")
    source = kwargs.get("source", "system_event")
    
    # Check for existing open alert
    existing_alert = None
    if agent_key:
        existing_alert = db.query(SystemAlert).filter(
            SystemAlert.agent_key == agent_key,
            SystemAlert.type == event_type,
            SystemAlert.source == source,
            SystemAlert.status == "open"
        ).first()
        
    if existing_alert:
        # Update existing alert
        existing_alert.updated_at = datetime.now()
        existing_alert.severity = severity # Update severity if changed
        existing_alert.description = description # Update description
        existing_alert.title = title # Update title
        
        # Merge metadata (especially supervisor analysis)
        new_metadata = kwargs.get("metadata", {})
        if existing_alert.alert_metadata:
            # We want to preserve remediation history and status if not explicitly overwritten
            current_meta = dict(existing_alert.alert_metadata)
            
            # Update supervisor analysis
            if "supervisor_analysis" in new_metadata:
                current_meta["supervisor_analysis"] = new_metadata["supervisor_analysis"]
                
            # Update other fields but preserve remediation state unless reset is needed
            # (Logic: if we are updating, the problem persists, so we might want to keep auto-remediation state
            # or reset it depending on specific rules. For now, we preserve it to avoid loops).
            
            existing_alert.alert_metadata = current_meta
        else:
            existing_alert.alert_metadata = new_metadata
            
        db.commit()
        db.refresh(existing_alert)
        return existing_alert
    else:
        # Create new alert
        return create_alert_from_event(
            db, 
            event_type=event_type, 
            severity=severity, 
            title=title, 
            description=description, 
            **kwargs
        )
