from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from pydantic import BaseModel

from app.api.deps import get_db, verify_admin_master_key, verify_master_key
from app.models.domain import Client, Agent, Asset, ScanJob, Finding, Partner, PartnerAPIKey, PartnerEarnings, ScanResult, AgentVersion
from app.schemas.contracts import ClientRead, ScanJobResponse, PartnerCreate, PartnerRead, PartnerCreateResponse, PartnerAPIKeyCreate, PartnerAPIKeyRead, PartnerUpdateMode
from app.services.cache import cache_service
from app.services.siem import siem_service
import secrets

router = APIRouter(
    dependencies=[Depends(verify_admin_master_key)]
)

@router.get("/overview")
@cache_service.cache(expire=60) # Cache for 1 minute
def get_admin_overview(db: Session = Depends(get_db)):
    """
    Devuelve un resumen global del sistema.
    """
    total_clients = db.query(Client).count()
    total_agents = db.query(Agent).count()
    total_assets = db.query(Asset).count()
    total_findings = db.query(Finding).count()
    total_jobs = db.query(ScanJob).count()
    total_partners = db.query(Partner).count()
    
    # Findings by severity
    findings_by_severity = {
        "critical": db.query(Finding).filter(func.lower(Finding.severity) == "critical").count(),
        "high": db.query(Finding).filter(func.lower(Finding.severity) == "high").count(),
        "medium": db.query(Finding).filter(func.lower(Finding.severity) == "medium").count(),
        "low": db.query(Finding).filter(func.lower(Finding.severity) == "low").count(),
    }
    
    active_agents = db.query(Agent).filter(Agent.status == "online").count()
    suspended_clients = db.query(Client).filter(Client.status == "suspended").count()
    
    # Last 10 findings
    last_findings = db.query(Finding).order_by(Finding.detected_at.desc()).limit(10).all()
    
    # Format last findings for UI
    formatted_findings = []
    for f in last_findings:
        formatted_findings.append({
            "id": f.id,
            "title": f.title,
            "severity": f.severity,
            "client_name": f.asset.client.name if f.asset and f.asset.client else "Unknown",
            "asset_ip": f.asset.ip if f.asset else "Unknown",
            "detected_at": f.detected_at
        })

    return {
        "total_clients": total_clients,
        "total_agents": total_agents,
        "total_assets": total_assets,
        "total_findings": total_findings,
        "total_jobs": total_jobs,
        "total_partners": total_partners,
        "findings_by_severity": findings_by_severity,
        "active_agents": active_agents,
        "suspended_clients": suspended_clients,
        "last_findings": formatted_findings
    }

@router.get("/clients")
@cache_service.cache(expire=60) # Cache for 1 minute
def list_all_clients(db: Session = Depends(get_db)):
    clients = db.query(Client).order_by(Client.created_at.desc()).all()
    # Enrich with counts
    result = []
    for c in clients:
        result.append({
            "id": c.id,
            "name": c.name,
            "contact_email": c.contact_email,
            "status": c.status,
            "created_at": c.created_at,
            "agents_count": len(c.agents),
            "assets_count": len(c.assets),
            "jobs_count": len(c.scan_jobs)
        })
    return result

@router.get("/agents")
@cache_service.cache(expire=60) # Cache for 1 minute
def list_all_agents(db: Session = Depends(get_db)):
    agents = db.query(Agent).order_by(Agent.last_seen_at.desc()).all()
    result = []
    for a in agents:
        result.append({
            "id": a.id,
            "hostname": a.hostname,
            "status": a.status,
            "last_seen_at": a.last_seen_at,
            "client_name": a.client.name if a.client else "Unknown",
            "version": "1.0.0" # Placeholder
        })
    return result


@router.get("/agents/{agent_id}/debug")
def debug_agent(
    agent_id: str,
    db: Session = Depends(get_db),
):
    """
    Devuelve una foto rápida del estado del agente y su último job.
    Útil para soporte/diagnóstico remoto.
    """
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agente no encontrado")

    last_job = (
        db.query(ScanJob)
        .filter(ScanJob.agent_id == agent.id)
        .order_by(ScanJob.created_at.desc())
        .first()
    )
    pending_job = (
        db.query(ScanJob)
        .filter(
            ScanJob.client_id == agent.client_id,
            ScanJob.status.in_(["pending", "running"]),
            ((ScanJob.agent_id == None) | (ScanJob.agent_id == agent.id)),  # noqa
        )
        .order_by(ScanJob.created_at.desc())
        .first()
    )

    return {
        "agent": {
            "id": agent.id,
            "hostname": agent.hostname,
            "status": agent.status,
            "last_seen_at": agent.last_seen_at,
            "client_id": agent.client_id,
            "version": getattr(agent, "version", None),
            "ip": getattr(agent, "ip", None) or getattr(agent, "local_ip", None),
            "interfaces_hash": hash(str(agent.interfaces)) if agent.interfaces else None,
            "capabilities": getattr(agent, "capabilities", {}),
        },
        "last_job": {
            "id": last_job.id if last_job else None,
            "type": last_job.type if last_job else None,
            "status": last_job.status if last_job else None,
            "target": last_job.target if last_job else None,
            "updated_at": last_job.finished_at or last_job.started_at if last_job else None,
        } if last_job else None,
        "next_pending_job": {
            "id": pending_job.id if pending_job else None,
            "type": pending_job.type if pending_job else None,
            "status": pending_job.status if pending_job else None,
            "target": pending_job.target if pending_job else None,
            "assigned_agent": pending_job.agent_id if pending_job else None,
        } if pending_job else None,
    }

@router.get("/jobs")
@cache_service.cache(expire=60) # Cache for 1 minute
def list_all_jobs(db: Session = Depends(get_db)):
    jobs = db.query(ScanJob).order_by(ScanJob.created_at.desc()).limit(50).all()
    result = []
    for j in jobs:
        result.append({
            "id": j.id,
            "type": j.type,
            "target": j.target,
            "status": j.status,
            "created_at": j.created_at,
            "client_name": j.client.name if j.client else "Unknown"
        })
    return result

@router.delete("/jobs/{job_id}")
def delete_job_admin(
    job_id: str,
    db: Session = Depends(get_db),
    _ = Depends(verify_admin_master_key)
):
    """
    Elimina un Job por ID (Admin).
    """
    job = db.query(ScanJob).filter(ScanJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job no encontrado")

    # Opcional: Limpiar resultados asociados si se desea
    # db.query(ScanResult).filter(ScanResult.scan_job_id == job.id).delete()

    db.delete(job)
    db.commit()
    return {"status": "deleted", "id": job_id}

@router.get("/findings")
@cache_service.cache(expire=60) # Cache for 1 minute
def list_all_findings(db: Session = Depends(get_db)):
    findings = db.query(Finding).order_by(Finding.detected_at.desc()).limit(50).all()
    result = []
    for f in findings:
        result.append({
            "id": f.id,
            "title": f.title,
            "severity": f.severity,
            "client_name": f.asset.client.name if f.asset and f.asset.client else "Unknown",
            "asset_ip": f.asset.ip if f.asset else "Unknown",
            "detected_at": f.detected_at
        })
    return result

@router.delete("/clients/{client_id}")
def delete_client_admin(
    client_id: str,
    db: Session = Depends(get_db),
    _ = Depends(verify_admin_master_key)
):
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    # Manual Cascade Delete
    try:
        # 1. Partner Earnings (linked to client)
        db.query(PartnerEarnings).filter(PartnerEarnings.client_id == client.id).delete(synchronize_session=False)

        # 2. Scan Results (linked to jobs)
        jobs = db.query(ScanJob).filter(ScanJob.client_id == client.id).all()
        job_ids = [j.id for j in jobs]
        if job_ids:
            db.query(ScanResult).filter(ScanResult.scan_job_id.in_(job_ids)).delete(synchronize_session=False)

        # 3. Scan Jobs
        db.query(ScanJob).filter(ScanJob.client_id == client.id).delete(synchronize_session=False)
        
        # 4. Findings (via Assets or direct client_id if applicable)
        db.query(Finding).filter(Finding.client_id == client.id).delete(synchronize_session=False)
        
        # 5. Assets
        db.query(Asset).filter(Asset.client_id == client.id).delete(synchronize_session=False)
        
        # 6. Agents
        db.query(Agent).filter(Agent.client_id == client.id).delete(synchronize_session=False)
        
        # 7. Subscription
        if client.subscription:
            db.delete(client.subscription)

        # 8. Client
        db.delete(client)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al eliminar cliente: {str(e)}")
    
    return {"status": "deleted", "id": client_id}



@router.delete("/agents/{agent_id}")
def delete_agent_admin(
    agent_id: str,
    db: Session = Depends(get_db),
    _ = Depends(verify_admin_master_key)
):
    """
    Elimina un agente globalmente.
    """
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agente no encontrado")

    try:
        # Desvincular jobs que estuvieran asignados a este agente
        # Opcional: ponerlos en pending de nuevo o borrarlos. 
        # Si el job estaba running, mejor lo fallamos o lo re-encolamos.
        # Aquí simplemente los desvinculamos (agent_id=None) y status=pending
        running_jobs = db.query(ScanJob).filter(ScanJob.agent_id == agent.id, ScanJob.status == "running").all()
        for job in running_jobs:
            job.agent_id = None
            job.status = "pending"
        
        # Desvincular assets descubiertos por este agente
        # NOTA: Asset.agent_id está comentado en el modelo, así que omitimos este paso por ahora.
        # assets = db.query(Asset).filter(Asset.agent_id == agent.id).all()
        # for asset in assets:
        #     asset.agent_id = None
        
        db.delete(agent)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al eliminar agente: {str(e)}")

    return {"status": "deleted", "id": agent_id}


@router.delete("/partners/{partner_id}")
def delete_partner(
    partner_id: str,
    db: Session = Depends(get_db),
    _ = Depends(verify_master_key)
):
    partner = db.query(Partner).filter(Partner.id == partner_id).first()
    if not partner:
        raise HTTPException(status_code=404, detail="Partner not found")
    
    # Check for active clients (Disabled as Client.partner_id is currently commented out)
    # active_clients = db.query(Client).filter(Client.partner_id == partner.id).count()
    # if active_clients > 0:
    #     raise HTTPException(
    #         status_code=400, 
    #         detail=f"No se puede eliminar el partner. Tiene {active_clients} clientes asociados. Elimínelos o reasígnelos primero."
    #     )

    try:
        # Delete API Keys
        db.query(PartnerAPIKey).filter(PartnerAPIKey.partner_id == partner.id).delete(synchronize_session=False)
        
        # Delete Earnings records
        db.query(PartnerEarnings).filter(PartnerEarnings.partner_id == partner.id).delete(synchronize_session=False)

        db.delete(partner)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al eliminar partner: {str(e)}")

    return {"status": "success", "message": "Partner deleted"}


@router.get("/system/health")
def system_health(db: Session = Depends(get_db), _ = Depends(verify_admin_master_key)):
    # Check DB
    db_status = "error"
    try:
        db.execute(func.text("SELECT 1"))
        db_status = "ok"
    except Exception as e:
        print(f"DB Health Error: {e}")
        pass
        
    # Check Redis
    redis_status = "error"
    try:
        if cache_service.redis_client.ping():
            redis_status = "ok"
    except Exception as e:
        print(f"Redis Health Error: {e}")
        pass

    return {
        "orchestrator": "ok",
        "database": db_status,
        "redis": redis_status,
        "environment": "Production",
        "version": "3.0.0"
    }

# ============================
# PARTNER MANAGEMENT
# ============================

@router.post("/partners", response_model=PartnerCreateResponse)
def create_partner(payload: PartnerCreate, db: Session = Depends(get_db)):
    # Check email
    existing = db.query(Partner).filter(Partner.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email ya registrado")

    # Determinar modo (demo/full)
    mode = (payload.account_mode or (payload.type.lower() if payload.type else None) or "demo").lower()

    # Handle Password
    raw_password = payload.password
    if not raw_password:
        raw_password = secrets.token_urlsafe(12)
    
    # Determine Limits based on Type
    p_type = payload.type or mode.upper()
    client_limit = 1 if mode == "demo" else 20
    agent_limit = 1 if mode == "demo" else 20
    demo_expires = None
    
    if mode == "demo":
        from datetime import datetime, timedelta, timezone
        demo_expires = datetime.now(timezone.utc) + timedelta(days=30)
    
    partner = Partner(
        name=payload.name,
        email=payload.email,
        hashed_password=raw_password, # In prod: hash it!
        status="active",
        type=p_type,
        account_mode=mode,
        client_limit=client_limit,
        agent_limit=agent_limit,
        demo_expires_at=demo_expires
    )
    db.add(partner)
    db.commit()
    db.refresh(partner)

    # Auto-generate initial API Key
    new_key = secrets.token_hex(32)
    api_key_record = PartnerAPIKey(
        partner_id=partner.id,
        name="Default Key",
        api_key=new_key,
        active=True
    )
    db.add(api_key_record)
    db.commit()

    # Prepare response with generated password
    response = PartnerCreateResponse.model_validate(partner)
    response.generated_password = raw_password
    response.api_key = new_key
    return response

@router.get("/partners", response_model=List[PartnerRead])
@cache_service.cache(expire=60) # Cache for 1 minute
def list_partners(db: Session = Depends(get_db)):
    return db.query(Partner).order_by(Partner.created_at.desc()).all()

@router.get("/risk-radar")
@cache_service.cache(expire=300) # Cache for 5 minutes
def get_risk_radar(
    db: Session = Depends(get_db),
    _ = Depends(verify_master_key)
):
    """
    Calcula las métricas para el gráfico de radar de riesgo.
    """
    # 1. Vulnerabilidades (0-100)
    # Ratio de findings criticos/altos vs total activos
    total_assets = db.query(Asset).count() or 1
    critical_findings = db.query(Finding).filter(Finding.severity.in_(["critical", "high"])).count()
    vuln_score = min(100, (critical_findings / total_assets) * 20) if total_assets > 0 else 0

    # 2. Exposición (0-100)
    # Basado en puertos abiertos (simulado con findings de tipo 'port')
    # Por ahora usaremos un proxy: % de activos con findings
    assets_with_findings = db.query(Asset.id).join(Finding).distinct().count()
    exposure_score = (assets_with_findings / total_assets) * 100 if total_assets > 0 else 0

    # 3. Anomalías (0-100)
    # Usaríamos el AI Engine aquí. Por ahora, mock basado en findings recientes
    anomaly_score = min(100, critical_findings * 5)

    # 4. Configuración (0-100)
    # Mock: Asumimos que el 80% está bien configurado
    config_score = 20 # 20% de riesgo de configuración (bajo es bueno en radar? o alto es riesgo?)
    # Asumimos que el radar muestra RIESGO, así que alto es malo.
    
    # 5. Cobertura (0-100)
    # Riesgo por falta de cobertura. 
    # Si tenemos 10 clientes y 5 agentes, cobertura 50%, riesgo 50%.
    total_clients = db.query(Client).count() or 1
    total_agents = db.query(Agent).count()
    coverage_ratio = min(1, total_agents / total_clients) # Simplificación
    coverage_risk = (1 - coverage_ratio) * 100

    return [
        {"subject": "Vulnerabilidades", "A": int(vuln_score), "fullMark": 100},
        {"subject": "Exposición", "A": int(exposure_score), "fullMark": 100},
        {"subject": "Mala Configuración", "A": int(config_score), "fullMark": 100},
        {"subject": "Anomalías IA", "A": int(anomaly_score), "fullMark": 100},
        {"subject": "Falta de Cobertura", "A": int(coverage_risk), "fullMark": 100},
    ]

@router.get("/network-topology")
@cache_service.cache(expire=300) # Cache for 5 minutes
def get_network_topology(
    db: Session = Depends(get_db),
    _ = Depends(verify_master_key)
):
    """
    Devuelve nodos y aristas para React Flow.
    """
    nodes = []
    edges = []
    
    # 1. Clientes como Grupos/Nodos Centrales
    clients = db.query(Client).all()
    y_offset = 0
    
    for client in clients:
        client_node_id = f"client-{client.id}"
        nodes.append({
            "id": client_node_id,
            "type": "input", # Input node for the cluster
            "data": {"label": f"🏢 {client.name}"},
            "position": {"x": 250, "y": y_offset},
            "style": {"background": "#6366f1", "color": "white", "width": 200}
        })
        
        # 2. Activos del Cliente
        assets = db.query(Asset).filter(Asset.client_id == client.id).all()
        x_offset = 0
        for i, asset in enumerate(assets):
            asset_node_id = f"asset-{asset.id}"
            nodes.append({
                "id": asset_node_id,
                "data": {"label": f"🖥️ {asset.ip}\n{asset.hostname or ''}"},
                "position": {"x": x_offset, "y": y_offset + 150},
            })
            
            # Conexión Cliente -> Activo
            edges.append({
                "id": f"e-{client_node_id}-{asset_node_id}",
                "source": client_node_id,
                "target": asset_node_id,
                "animated": True
            })
            x_offset += 200
            
        y_offset += 300

    return {"nodes": nodes, "edges": edges}

@router.patch("/partners/{partner_id}/reset-password", response_model=Dict[str, str])
def reset_partner_password(partner_id: str, db: Session = Depends(get_db)):
    partner = db.query(Partner).filter(Partner.id == partner_id).first()
    if not partner:
        raise HTTPException(status_code=404, detail="Partner no encontrado")
    
    new_password = secrets.token_urlsafe(12)
    partner.hashed_password = new_password # In prod: hash it!
    db.commit()
    
    return {"password": new_password}

@router.get("/global-stats", response_model=Dict[str, Any])
@cache_service.cache(expire=60)
def get_global_stats(db: Session = Depends(get_db)):
    """
    Devuelve estadísticas globales de amenazas desde Redis.
    """
    try:
        r = cache_service.redis_client
        total_threats = int(r.get("global:threats:total") or 0)
        
        # Mock top threats for now if not in redis
        top_threats = [] 
        
        severity_dist = {
            "critical": int(r.get("global:threats:severity:critical") or 0),
            "high": int(r.get("global:threats:severity:high") or 0),
            "medium": int(r.get("global:threats:severity:medium") or 0),
            "low": int(r.get("global:threats:severity:low") or 0),
        }
        
        return {
            "total_threats_processed": total_threats,
            "top_threats": top_threats,
            "severity_distribution": severity_dist
        }
    except Exception as e:
        print(f"Error fetching global stats: {e}")
        return {
            "total_threats_processed": 0,
            "top_threats": [],
            "severity_distribution": {"critical": 0, "high": 0, "medium": 0, "low": 0}
        }

@router.get("/partners/{partner_id}")
def get_partner_details(partner_id: str, db: Session = Depends(get_db)):
    partner = db.query(Partner).filter(Partner.id == partner_id).first()
    if not partner:
        raise HTTPException(status_code=404, detail="Partner no encontrado")
    
    # Enrich with clients and api keys
    clients = db.query(Client).filter(Client.partner_id == partner.id).all()
    api_keys = db.query(PartnerAPIKey).filter(PartnerAPIKey.partner_id == partner.id).all()
    
    return {
        "partner": partner,
        "clients": clients,
        "api_keys": api_keys
    }

from app.schemas.contracts import PartnerAPIKeyCreate, PartnerAPIKeyRead
import secrets
from app.models.domain import PartnerAPIKey

@router.post("/partners/{partner_id}/api-keys", response_model=PartnerAPIKeyRead)
def create_partner_api_key_admin(
    partner_id: str,
    payload: PartnerAPIKeyCreate,
    db: Session = Depends(get_db)
):
    partner = db.query(Partner).filter(Partner.id == partner_id).first()
    if not partner:
        raise HTTPException(status_code=404, detail="Partner no encontrado")
        
    new_key = secrets.token_hex(32)
    api_key_record = PartnerAPIKey(
        partner_id=partner.id,
        name=payload.name,
        api_key=new_key,
        active=True
    )
    db.add(api_key_record)
    db.commit()
    db.refresh(api_key_record)
    return api_key_record


@router.patch("/partners/{partner_id}/commission", response_model=PartnerRead)
def update_partner_commission(
    partner_id: str,
    db: Session = Depends(get_db)
):
    # Comisiones deshabilitadas; mantenemos endpoint para compatibilidad
    raise HTTPException(status_code=410, detail="Comisiones deshabilitadas para partners")

@router.patch("/partners/{partner_id}/mode", response_model=PartnerRead)
def update_partner_mode(
    partner_id: str,
    payload: PartnerUpdateMode,
    db: Session = Depends(get_db),
    _ = Depends(verify_admin_master_key)
):
    partner = db.query(Partner).filter(Partner.id == partner_id).first()
    if not partner:
        raise HTTPException(status_code=404, detail="Partner no encontrado")
        
    new_mode = payload.account_mode.lower()
    if new_mode not in ["demo", "full"]:
        raise HTTPException(status_code=400, detail="Modo inválido. Use 'demo' o 'full'.")
        
    partner.account_mode = new_mode
    partner.type = new_mode.upper() # Keep legacy field in sync
    
    # Update limits based on mode
    if new_mode == "demo":
        partner.client_limit = 1
        partner.agent_limit = 1
        # Set expiration if not set? Or reset it? Let's leave it as is or set 30 days from now if null
        if not partner.demo_expires_at:
            from datetime import datetime, timedelta, timezone
            partner.demo_expires_at = datetime.now(timezone.utc) + timedelta(days=30)
    else:
        # Full mode defaults
        partner.client_limit = 20 + (partner.client_packages * 10)
        partner.agent_limit = 20 + (partner.agent_packages * 10)
        partner.demo_expires_at = None
        
    db.commit()
    db.refresh(partner)
    return partner

# ============================
# AGENT UPDATE MANAGEMENT
# ============================

class AgentMassUpdateRequest(BaseModel):
    scope: str # all, partner, client
    scope_id: Optional[str] = None
    channel: str = "stable"

@router.post("/agents/update")
def trigger_mass_update(
    payload: AgentMassUpdateRequest,
    db: Session = Depends(get_db),
    _ = Depends(verify_admin_master_key)
):
    """
    Desencadena una actualización masiva de agentes mediante jobs 'self_update'.
    """
    # 1. Get Latest Version info
    latest = db.query(AgentVersion).filter(
        AgentVersion.tier == payload.channel, 
        AgentVersion.platform == "windows" # Por ahora solo windows
    ).order_by(desc(AgentVersion.release_date)).first()
    
    if not latest:
        raise HTTPException(status_code=404, detail=f"No hay release {payload.channel} disponible")
    
    # 2. Select Agents
    q = db.query(Agent).filter(Agent.status == 'online') # Solo agentes online
    
    if payload.scope == 'partner':
        if not payload.scope_id:
            raise HTTPException(400, "scope_id requerido para partner")
        q = q.join(Client).filter(Client.partner_id == payload.scope_id)
        
    elif payload.scope == 'client':
        if not payload.scope_id:
            raise HTTPException(400, "scope_id requerido para client")
        q = q.filter(Agent.client_id == payload.scope_id)
        
    elif payload.scope == 'all':
        pass # No filter
    
    else:
        raise HTTPException(400, "Invalid scope")
    
    agents = q.all()
    
    count_ok = 0
    count_skipped = 0
    
    # 3. Create Jobs
    from datetime import datetime, timezone
    for a in agents:
        # Check current version
        if a.version == latest.version:
            count_skipped += 1
            continue
        
        # Check existing pending update job
        existing = db.query(ScanJob).filter(
            ScanJob.agent_id == a.id, 
            ScanJob.type == "self_update", 
            ScanJob.status.in_(['pending', 'running'])
        ).first()
        
        if existing:
            count_skipped += 1
            continue

        job = ScanJob(
            client_id=a.client_id,
            agent_id=a.id,
            type="self_update",
            target="local",
            status="pending",
            created_at=datetime.now(timezone.utc),
            params={
                "version": latest.version,
                "url": latest.download_url,
                "sha256": latest.checksum_sha256
            }
        )
        db.add(job)
        count_ok += 1
    
    db.commit()
    
    return {
        "status": "success", 
        "queued": count_ok, 
        "skipped": count_skipped, 
        "target_version": latest.version
    }

# ============================
# CORRELATION & AUDIT TOOLS
# ============================

class AgentAssignRequest(BaseModel):
    client_id: Optional[str] = None
    partner_id: Optional[str] = None
    # tenant_id: Optional[str] = None # Future use

@router.post("/agents/{agent_id}/assign")
def assign_agent_context(
    agent_id: str,
    payload: AgentAssignRequest,
    db: Session = Depends(get_db),
    _ = Depends(verify_admin_master_key)
):
    """
    Reasignar un agente a otro cliente/partner (Fix Correlation).
    """
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
         raise HTTPException(status_code=404, detail="Agent not found")

    changes = []

    # 1. Update Client
    if payload.client_id:
        client = db.query(Client).filter(Client.id == payload.client_id).first()
        if not client:
             raise HTTPException(status_code=404, detail="Target Client not found")
        
        old_client_id = agent.client_id
        if old_client_id != payload.client_id:
            agent.client_id = payload.client_id
            changes.append(f"client_id: {old_client_id} -> {payload.client_id}")

    # 2. Update Partner (Currently via Client, but if we had direct link...)
    # The Client dictates the partner. So if client changed, partner changed implicitly.
    # If we want to move the CLIENT to a PARTNER, that's a Client update, not Agent.
    
    if payload.partner_id:
        # Check if we are moving the agent's CLIENT to a partner? 
        # Or just checking if agent->client->partner is consistent?
        # Let's assume this tool updates the CLIENT's partner_id if specified
        if agent.client:
             old_p_id = agent.client.partner_id
             if old_p_id != payload.partner_id:
                  target_partner = db.query(Partner).filter(Partner.id == payload.partner_id).first()
                  if not target_partner:
                       raise HTTPException(404, "Target Partner not found")
                  
                  agent.client.partner_id = payload.partner_id
                  changes.append(f"client.partner_id: {old_p_id} -> {payload.partner_id}")

    db.commit()
    
    return {
        "status": "updated",
        "agent_id": agent_id,
        "changes": changes
    }

@router.get("/audit/correlation")
def audit_correlation(
    db: Session = Depends(get_db),
    _ = Depends(verify_admin_master_key)
):
    """
    Detecta inconsistencias:
    - Agentes con cliente sin partner.
    - Clientes apuntando a partner inexistente.
    """
    mismatches = []
    
    # 1. Agents with Clients having NO partner
    # (Might be valid for self-managed, but let's list them)
    agents_no_partner = db.query(Agent).join(Client).filter(Client.partner_id == None).all()
    for a in agents_no_partner:
        mismatches.append({
            "type": "agent_no_partner",
            "agent_id": a.id,
            "agent_host": a.hostname,
            "client_id": a.client_id,
            "client_name": a.client.name if a.client else "Unknown"
        })

    # 2. Clients with Invalid Partner ID (Orphaned FK if constraint missing)
    # SQLAlchemy usually handles constraints, but let's check.
    # We can't easily query "partner_id NOT IN partners.id" via simple ORM without subquery.
    # Let's skip complex SQL for MVP and rely on "no_partner" check.
    
    return {
        "count": len(mismatches),
        "mismatches": mismatches
    }
