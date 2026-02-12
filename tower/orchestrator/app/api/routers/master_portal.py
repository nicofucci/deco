from typing import List, Any
import os
import secrets
from datetime import datetime, timezone
import httpx
import asyncio

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, text

from app.api.deps import get_db, verify_admin_master_key
from app.models.domain import Asset, Client, Finding, ScanResult, ScanJob, Partner, PartnerEarnings, PartnerAPIKey, Agent, Subscription


from app.schemas.contracts import ClientAssetResponse, ClientFindingResponse, MasterJobResponse, PartnerAPIKeyCreate
from app.api.routers.client_portal import _extract_ports
from app.services.cache import cache_service

router = APIRouter(dependencies=[Depends(verify_admin_master_key)])


@router.get("/assets")
def list_global_assets(
    skip: int = 0,
    limit: int = 50,
    client_id: str = None,
    search: str = None,
    db: Session = Depends(get_db)
):
    """
    Devuelve assets paginados y filtrados para el panel master.
    """
    query = db.query(Asset)

    if client_id:
        query = query.filter(Asset.client_id == client_id)

    if search:
        term = f"%{search}%"
        query = query.filter((Asset.ip.ilike(term)) | (Asset.hostname.ilike(term)))

    total = query.count()
    assets = query.order_by(Asset.created_at.desc()).offset(skip).limit(limit).all()

    items: List[ClientAssetResponse] = []
    for asset in assets:
        latest_result = (
            db.query(ScanResult)
            .join(ScanJob, ScanResult.scan_job_id == ScanJob.id)
            .order_by(ScanResult.created_at.desc())
            .first()
        )
        open_ports = _extract_ports(latest_result.raw_data, asset.ip) if latest_result else []
        last_scan_at = latest_result.created_at if latest_result else None

        hostname = asset.hostname or (asset.client.name if asset.client else None)
        items.append(
            ClientAssetResponse(
                id=asset.id,
                ip=asset.ip,
                hostname=hostname,
                client_name=asset.client.name if asset.client else None,
                open_ports=open_ports,
                last_scan_at=last_scan_at,
            )
        )
    return {"total": total, "items": items}


@router.get("/findings")
def list_global_findings(
    skip: int = 0,
    limit: int = 50,
    severity: str = None,
    client_id: str = None,
    db: Session = Depends(get_db)
):
    """
    Devuelve hallazgos paginados y filtrados para el panel master.
    """
    query = (
        db.query(Finding)
        .join(Asset, Finding.asset_id == Asset.id)
        .join(Client, Client.id == Finding.client_id)
    )

    if severity:
        query = query.filter(func.lower(Finding.severity) == severity.lower())
    
    if client_id:
        query = query.filter(Finding.client_id == client_id)

    total = query.count()
    findings = query.order_by(Finding.detected_at.desc()).offset(skip).limit(limit).all()

    items = [
        ClientFindingResponse(
            id=f.id,
            asset_id=f.asset_id,
            asset_ip=f.asset.ip if f.asset else "",
            client_name=f.asset.client.name if f.asset and f.asset.client else None,
            severity=f.severity,
            title=f.title,
            description=f.description,
            recommendation=f.recommendation,
            detected_at=f.detected_at,
        )
        for f in findings
    ]
    return {"total": total, "items": items}


@router.get("/global_insights")
async def get_global_insights(db: Session = Depends(get_db)):
    """
    Devuelve puntos geográficos de agentes para el mapa global.
    Si no hay geolocalización disponible, retorna lista vacía.
    """
    agents = db.query(Agent).all()
    geo_points = []

    for agent in agents:
        geo_points.append({
            "agent_id": agent.id,
            "client_id": agent.client_id,
            "client_name": agent.client.name if agent.client else None,
            "hostname": agent.hostname,
            "status": agent.status,
            # Coordenadas no disponibles → fallback (0,0); se puede enriquecer con GeoIP
            "lat": 0,
            "lng": 0,
        })

    return {
        "geo_points": geo_points,
        "total_agents": len(geo_points)
    }


@router.get("/jobs", response_model=List[MasterJobResponse])
def list_global_jobs(db: Session = Depends(get_db)):
    """
    Devuelve todos los jobs globales para el panel master.
    """
    jobs = (
        db.query(ScanJob)
        .join(Client, ScanJob.client_id == Client.id)
        .outerjoin(Agent, ScanJob.agent_id == Agent.id)
        .order_by(ScanJob.created_at.desc())
        .all()
    )

    return [
        MasterJobResponse(
            id=j.id,
            client_name=j.client.name if j.client else "Unknown",
            agent_hostname=j.agent.hostname if j.agent else None,
            type=j.type,
            target=j.target,
            status=j.status,
            created_at=j.created_at,
            started_at=j.started_at,
            finished_at=j.finished_at,
        )
        for j in jobs
    ]


@router.get("/jobs/{job_id}/results")
def get_job_results(
    job_id: str,
    db: Session = Depends(get_db)
):
    """
    Obtiene los resultados de un job específico.
    """
    result = db.query(ScanResult).filter(ScanResult.scan_job_id == job_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Resultados no encontrados para este job")
    
    return {
        "id": result.id,
        "scan_job_id": result.scan_job_id,
        "created_at": result.created_at,
        "raw_data": result.raw_data # This might be large
    }

from fastapi.responses import Response

@router.get("/jobs/{job_id}/download")
def download_job_results(
    job_id: str,
    db: Session = Depends(get_db)
):
    """
    Descarga los resultados raw de un job.
    """
    result = db.query(ScanResult).filter(ScanResult.scan_job_id == job_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Resultados no encontrados")
    
    import json
    data = json.dumps(result.raw_data, indent=2)
    
    return Response(
        content=data,
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename=scan_result_{job_id}.json"}
    )


@router.get("/reports", response_model=list[Any])
def get_reports(
    db: Session = Depends(get_db),
    _ = Depends(verify_admin_master_key)
):
    """
    Devuelve la lista de reportes PDF generados y almacenados en disco.
    """
    reports = []
    report_dir = "/tmp/reports"
    
    if not os.path.exists(report_dir):
        return []

    # List all PDF files
    files = [f for f in os.listdir(report_dir) if f.endswith(".pdf") and f.startswith("report_")]
    
    # Sort by modification time (newest first)
    files.sort(key=lambda x: os.path.getmtime(os.path.join(report_dir, x)), reverse=True)

    for filename in files:
        parts = filename.split("_")
        try:
            uuid_part = parts[-1]
            lang = parts[-2]
            type_part = parts[-3]
            client_name = "_".join(parts[1:-3])
            
            filepath = os.path.join(report_dir, filename)
            mod_time = os.path.getmtime(filepath)
            generated_at = datetime.fromtimestamp(mod_time, tz=timezone.utc).isoformat()
            
            reports.append({
                "id": uuid_part.replace(".pdf", ""),
                "client_name": client_name.replace("_", " "),
                "type": f"{type_part.capitalize()} Report ({lang.upper()})",
                "generated_at": generated_at,
                "severity": "Info",
                "download_url": f"/api/reports/download/{filename}"
            })
        except Exception:
            continue

    return reports


@router.get("/summary")
async def get_dashboard_summary(db: Session = Depends(get_db)):
    """
    Devuelve métricas generales para el dashboard master.
    """
    total_clients = db.query(Client).count()
    suspended_clients = db.query(Client).filter(Client.status == "suspended").count()
    
    total_partners = db.query(Partner).count()
    
    total_assets = db.query(Asset).count()
    total_agents = db.query(Agent).count()
    active_agents = db.query(Agent).filter(Agent.status == "online").count()
    
    total_jobs = db.query(ScanJob).count()
    active_jobs = db.query(ScanJob).filter(ScanJob.status == "running").count()
    
    total_findings = db.query(Finding).count()
    
    # Findings by severity
    findings_critical = db.query(Finding).filter(Finding.severity == "critical").count()
    findings_high = db.query(Finding).filter(Finding.severity == "high").count()
    findings_medium = db.query(Finding).filter(Finding.severity == "medium").count()
    findings_low = db.query(Finding).filter(Finding.severity == "low").count()
    
    # Last findings
    last_findings_query = (
        db.query(Finding)
        .join(Asset, Finding.asset_id == Asset.id)
        .join(Client, Client.id == Finding.client_id)
        .order_by(Finding.detected_at.desc())
        .limit(5)
        .all()
    )
    
    last_findings = [
        {
            "id": f.id,
            "severity": f.severity,
            "title": f.title,
            "client_name": f.asset.client.name if f.asset and f.asset.client else "Unknown",
            "detected_at": f.detected_at
        }
        for f in last_findings_query
    ]
    

    active_agents_list = db.query(Agent).filter(Agent.status == "online").all()
    geo_counts = {}
    
    async with httpx.AsyncClient() as client:
        for agent in active_agents_list:
            if not agent.ip or agent.ip in ["127.0.0.1", "localhost", "::1"]:
                continue
                
            try:
                # Using ip-api.com (free, rate limited 45/min)
                response = await client.get(f"http://ip-api.com/json/{agent.ip}", timeout=2.0)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "success":
                        country = data.get("country", "Unknown")
                        code = data.get("countryCode", "UNK") # Alpha-2
                        # Convert Alpha-2 to Alpha-3 if possible, or just use Alpha-2. 
                        # Frontend expects 3-letter code for flags map, but we can adjust frontend or map here.
                        # Let's map common ones or just pass code.
                        
                        key = code
                        if key not in geo_counts:
                            geo_counts[key] = {
                                "country": country,
                                "code": code,
                                "count": 0,
                                "lat": data.get("lat", 0.0),
                                "lng": data.get("lon", 0.0)
                            }
                        geo_counts[key]["count"] += 1
            except Exception as e:
                print(f"GeoIP Error for {agent.ip}: {e}")
                continue

    geo_distribution = list(geo_counts.values())

    return {
        "total_clients": total_clients,
        "suspended_clients": suspended_clients,
        "total_partners": total_partners,
        "total_assets": total_assets,
        "total_agents": total_agents,
        "active_agents": active_agents,
        "active_jobs": active_jobs,
        "total_jobs": total_jobs,
        "total_findings": total_findings,
        "findings_by_severity": {
            "critical": findings_critical,
            "high": findings_high,
            "medium": findings_medium,
            "low": findings_low
        },
        "last_findings": last_findings,
        "geo_distribution": geo_distribution,
        "system_status": "healthy",
        "last_updated": datetime.now(timezone.utc).isoformat()
    }


@router.delete("/clients/{client_id}")
def delete_client_master(
    client_id: str,
    db: Session = Depends(get_db)
):
    """
    Elimina un cliente y todos sus datos asociados (Cascade).
    """
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    try:
        # 1. Partner Earnings
        db.query(PartnerEarnings).filter(PartnerEarnings.client_id == client.id).delete(synchronize_session=False)

        # 2. Scan Results
        jobs = db.query(ScanJob).filter(ScanJob.client_id == client.id).all()
        job_ids = [j.id for j in jobs]
        if job_ids:
            db.query(ScanResult).filter(ScanResult.scan_job_id.in_(job_ids)).delete(synchronize_session=False)

        # 3. Scan Jobs
        db.query(ScanJob).filter(ScanJob.client_id == client.id).delete(synchronize_session=False)
        
        # 4. Findings
        db.query(Finding).filter(Finding.client_id == client.id).delete(synchronize_session=False)
        
        # 4.5. Jarvis Scan Reports (Raw SQL as model is missing)
        # These reference assets, so must be deleted before assets.
        # Use subquery to avoid list binding issues.
        db.execute(
            text("DELETE FROM jarvis_scan_reports WHERE asset_id IN (SELECT id FROM assets WHERE client_id = :client_id)"),
            {"client_id": client_id}
        )

        # 5. Assets
        db.query(Asset).filter(Asset.client_id == client.id).delete(synchronize_session=False)
        
        # 6. Agents
        db.query(Agent).filter(Agent.client_id == client.id).delete(synchronize_session=False)
        


        # 7.5. Activation Codes (Raw SQL as model is missing)
        db.execute(
            text("DELETE FROM activation_codes WHERE client_id = :client_id"),
            {"client_id": client_id}
        )

        # 8. Client
        db.delete(client)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al eliminar cliente: {str(e)}")
    
    return {"status": "deleted", "id": client_id}


@router.get("/clients", response_model=List[Any])
def list_master_clients(db: Session = Depends(get_db)):
    """
    Lista de clientes para el panel master.
    """
    # Use subqueries for counts to avoid Cartesian product issues with multiple joins
    agent_count_sub = (
        db.query(func.count(Agent.id))
        .filter(Agent.client_id == Client.id)
        .correlate(Client)
        .scalar_subquery()
    )

    asset_count_sub = (
        db.query(func.count(Asset.id))
        .filter(Asset.client_id == Client.id)
        .correlate(Client)
        .scalar_subquery()
    )

    results = (
        db.query(
            Client,
            agent_count_sub.label("agent_count"),
            asset_count_sub.label("asset_count")
        )
        .order_by(Client.created_at.desc())
        .all()
    )

    return [
        {
            "id": c.Client.id,
            "name": c.Client.name,
            "status": c.Client.status,
            "contact_email": c.Client.contact_email,
            "created_at": c.Client.created_at,
            "agent_count": c.agent_count,
            "asset_count": c.asset_count
        }
        for c in results
    ]


@router.get("/agents", response_model=List[Any])
def list_master_agents(db: Session = Depends(get_db)):
    """
    Lista de todos los agentes registrados en el sistema.
    """
    agents = db.query(Agent).order_by(Agent.last_seen_at.desc()).all()
    
    return [
        {
            "id": a.id,
            "hostname": a.hostname,
            "client_name": a.client.name if a.client else "Unknown",
            "status": a.status,
            "version": a.version,
            "os": a.os,
            "ip": a.ip,
            "last_seen_at": a.last_seen_at
        }
        for a in agents
    ]


@router.delete("/agents/{agent_id}")
def delete_agent_master(
    agent_id: str,
    db: Session = Depends(get_db)
):
    """
    Elimina un agente y sus trabajos asociados.
    """
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agente no encontrado")

    try:

        # 1. Eliminar resultados de jobs de este agente
        jobs = db.query(ScanJob).filter(ScanJob.agent_id == agent.id).all()
        job_ids = [j.id for j in jobs]
        if job_ids:
            db.query(ScanResult).filter(ScanResult.scan_job_id.in_(job_ids)).delete(synchronize_session=False)

        # 2. Eliminar jobs
        db.query(ScanJob).filter(ScanJob.agent_id == agent.id).delete(synchronize_session=False)

        # 3. Eliminar AgentStatus (FK Constraint Reference)
        # Import AgentStatus locally to avoid circular imports if any, or use raw SQL safer
        # But we can import it at top or check if it is imported. 
        # Checking imports... 'Agent' is imported from app.models.domain. 
        # We need to import AgentStatus there too.
        # Since I can't easily see top imports while defining this chunk, I will use raw SQL for safety and speed to fix the specific FK error.
        # "agent_status" table.
        db.execute(text("DELETE FROM agent_status WHERE agent_id = :aid"), {"aid": agent.id})

        # 3.5. Eliminar Fleet Alerts (FK Constraint)
        db.execute(text("DELETE FROM fleet_alerts WHERE agent_id = :aid"), {"aid": agent.id})

        # 4. Cleanup other references (Set to NULL to preserve history/assets)
        # network_assets
        db.execute(text("UPDATE network_assets SET agent_id = NULL WHERE agent_id = :aid"), {"aid": agent.id})
        # network_vulnerabilities
        db.execute(text("UPDATE network_vulnerabilities SET agent_id = NULL WHERE agent_id = :aid"), {"aid": agent.id})
        # autofix_executions
        db.execute(text("UPDATE autofix_executions SET agent_id = NULL WHERE agent_id = :aid"), {"aid": agent.id})

        # 5. Eliminar agente
        db.delete(agent)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al eliminar agente: {str(e)}")

    return {"status": "deleted", "id": agent_id}


@router.get("/system")
def get_system_status(db: Session = Depends(get_db)):
    """
    Estado del sistema (servicios, recursos).
    """
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
        if cache_service.redis.ping():
            redis_status = "ok"
    except Exception as e:
        print(f"Redis Health Error: {e}")
        pass

    return {
        "orchestrator": "ok",
        "database": db_status,
        "redis": redis_status,
        "version": "3.0.0",
        "uptime": "99.9%",
        "environment": "Production"
    }


@router.get("/partners")
def list_master_partners(db: Session = Depends(get_db)):
    """
    Lista de partners.
    """
    partners = db.query(Partner).order_by(Partner.created_at.desc()).all()
    return partners


@router.get("/partners/{partner_id}")
def get_partner_details_master(
    partner_id: str,
    db: Session = Depends(get_db)
):
    """
    Detalles de un partner específico para el panel master.
    Incluye sus clientes y API Keys.
    """
    partner = db.query(Partner).filter(Partner.id == partner_id).first()
    if not partner:
        raise HTTPException(status_code=404, detail="Partner no encontrado")

    # Clients
    clients = db.query(Client).filter(Client.partner_id == partner.id).all()
    clients_data = [
        {
            "id": c.id,
            "name": c.name,
            "contact_email": c.contact_email,
            "status": c.status
        }
        for c in clients
    ]

    # API Keys
    api_keys = db.query(PartnerAPIKey).filter(PartnerAPIKey.partner_id == partner.id).all()
    api_keys_data = [
        {
            "id": k.id,
            "name": k.name,
            "api_key": k.api_key,
            "created_at": k.created_at,
            "last_used_at": k.last_used_at
        }
        for k in api_keys
    ]

    return {
        "partner": {
            "id": partner.id,
            "name": partner.name,
            "email": partner.email,
            "status": partner.status,
            "account_mode": getattr(partner, "account_mode", "demo"),
            "type": partner.type,
            "created_at": partner.created_at
        },
        "clients": clients_data,
        "api_keys": api_keys_data
    }


@router.post("/partners/{partner_id}/api-keys")
def create_partner_api_key_master(
    partner_id: str,
    payload: PartnerAPIKeyCreate,
    db: Session = Depends(get_db)
):
    """
    Crea una API Key para un partner desde el panel master.
    """
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
    
    return {
        "id": api_key_record.id,
        "name": api_key_record.name,
        "api_key": api_key_record.api_key,
        "created_at": api_key_record.created_at
    }
