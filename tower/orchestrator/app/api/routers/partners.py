from typing import List, Optional
import secrets
from datetime import datetime, timedelta, timezone
import uuid
import os

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.api.deps import get_db, get_current_partner_from_token, get_partner_from_api_key
from app.models.domain import Partner, Client, PartnerAPIKey, PartnerEarnings, Agent, Asset, Finding, ScanJob, ReportSnapshot, NetworkAsset, NetworkVulnerability, ReportSnapshotFinding, AgentVersion
from app.api.utils import compute_agent_online_status
from app.schemas.contracts import (
    PartnerRead, PartnerLoginRequest, PartnerLoginResponse,
    ClientCreate, ClientRead, PartnerAPIKeyCreate, PartnerAPIKeyRead, PartnerEarningsSummary,
    PackagePurchaseRequest, PartnerBillingSummary, PartnerScanRequest, PartnerAgentActionRequest,
    ScanJobResponse, ReportResponse, PartnerReportRequest, ClientFindingResponse
)
from pydantic import BaseModel
from app.services.reports import ReportGenerator

router = APIRouter()

# ============================
# PARTNER MANAGEMENT (ADMIN)
# ============================

@router.get("/", response_model=List[PartnerRead])
def list_partners(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
    # In a real app, we should protect this with Admin Master Key
):
    partners = db.query(Partner).offset(skip).limit(limit).all()
    return partners

@router.post("/", response_model=PartnerRead)
def create_partner(
    payload: PartnerLoginRequest, # Reusing schema for simplicity, ideally PartnerCreate
    db: Session = Depends(get_db)
):
    # Check if exists
    existing = db.query(Partner).filter(Partner.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="El partner ya existe")
        
    new_partner = Partner(
        name=payload.email.split("@")[0], # Default name
        email=payload.email,
        hashed_password=payload.password,
        status="active",
        partner_api_key=secrets.token_hex(16),
        created_at=datetime.utcnow()
    )
    db.add(new_partner)
    db.commit()
    db.refresh(new_partner)
    return new_partner

# ============================
# AUTHENTICATION
# ============================

class PartnerValidateKeyRequest(BaseModel):
    api_key: str

@router.post("/validate-key", response_model=PartnerLoginResponse)
def validate_partner_key(payload: PartnerValidateKeyRequest, db: Session = Depends(get_db)):
    partner = db.query(Partner).filter(Partner.partner_api_key == payload.api_key).first()
    if not partner:
        # Fallback check in PartnerAPIKey table for backward compatibility or if used there
        key_record = db.query(PartnerAPIKey).filter(PartnerAPIKey.api_key == payload.api_key).first()
        if key_record and key_record.active:
            partner = key_record.partner
            
    if not partner:
        raise HTTPException(status_code=401, detail="API Key inválida")
        
    if partner.status != "active":
        raise HTTPException(status_code=403, detail="Cuenta suspendida")
        
    return {
        "access_token": partner.partner_api_key, 
        "token_type": "bearer",
        "partner_id": partner.id,
        "name": partner.name,
        "email": partner.email,
        "account_mode": getattr(partner, "account_mode", "demo")
    }

@router.post("/login", response_model=PartnerLoginResponse)
def login_partner(payload: PartnerLoginRequest, db: Session = Depends(get_db)):
    partner = db.query(Partner).filter(Partner.email == payload.email).first()
    if not partner or partner.hashed_password != payload.password: # In prod: verify_password
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
        
    if partner.status != "active":
        raise HTTPException(status_code=403, detail="Cuenta suspendida")
        
    # Simplified token for MVP: return the API Key so it can be used in X-Partner-API-Key header
    return {
        "access_token": partner.partner_api_key,
        "token_type": "bearer",
        "partner_id": partner.id,
        "name": partner.name,
        "email": partner.email,
        "account_mode": getattr(partner, "account_mode", "demo")
    }

# ============================
# PARTNER SELF-MANAGEMENT
# ============================

@router.get("/me", response_model=PartnerRead)
def get_me(partner: Partner = Depends(get_partner_from_api_key)):
    return partner

@router.get("/me/earnings", response_model=PartnerEarningsSummary)
def get_earnings(partner: Partner = Depends(get_partner_from_api_key), db: Session = Depends(get_db)):
    # Calculate Source of Truth for Agents
    limit = partner.agent_limit
    assigned = (
        db.query(func.count(Agent.id))
        .join(Client)
        .filter(Client.partner_id == partner.id)
        .scalar()
    ) or 0
    available = max(0, limit - assigned)

    return {
        "total_clients_active": db.query(Client).filter(Client.partner_id == partner.id, Client.status == "active").count(),
        "total_earnings_lifetime": 0.0,
        "total_earnings_last_month": 0.0,
        "earnings_history": [],
        "message": "Sistema de comisiones deshabilitado. Próximamente ingresos por paquetes.",
        "agents_limit": limit,
        "agents_assigned": assigned,
        "agents_available": available
    }

@router.post("/me/packages")
def buy_packages(
    payload: PackagePurchaseRequest,
    partner: Partner = Depends(get_partner_from_api_key),
    db: Session = Depends(get_db)
):
    if getattr(partner, "account_mode", partner.type.lower()) != "full":
        raise HTTPException(status_code=403, detail="Solo los partners Full pueden comprar paquetes.")
    
    if payload.quantity != 1:
        raise HTTPException(status_code=400, detail="Los paquetes se compran de 1 en 1 (10 unidades).")

    if payload.type == "clients":
        partner.client_packages += 1
        partner.client_limit += 10
    elif payload.type == "agents":
        partner.agent_packages += 1
        partner.agent_limit += 10
    else:
        raise HTTPException(status_code=400, detail="Tipo de paquete inválido.")
    
    db.commit()
    db.refresh(partner)
    return {"status": "success", "message": "Paquete comprado exitosamente", "new_limits": {"clients": partner.client_limit, "agents": partner.agent_limit}}

@router.get("/me/billing", response_model=PartnerBillingSummary)
def get_billing_summary(partner: Partner = Depends(get_partner_from_api_key)):
    base_price = 297.0
    client_pkg_price = 150.0
    agent_pkg_price = 10.0
    
    total = base_price + (partner.client_packages * client_pkg_price) + (partner.agent_packages * agent_pkg_price)
    
    return {
        "base_plan": base_price,
        "paquetes_clientes": partner.client_packages,
        "paquetes_agentes": partner.agent_packages,
        "total_clientes_permitidos": partner.client_limit,
        "total_agentes_permitidos": partner.agent_limit,
        "facturacion_total": total
    }

# ============================
# CLIENT MANAGEMENT
# ============================

@router.get("/me/clients", response_model=List[dict])
def list_my_clients(partner: Partner = Depends(get_partner_from_api_key), db: Session = Depends(get_db)):
    clients = db.query(Client).filter(Client.partner_id == partner.id).order_by(Client.created_at.desc()).all()
    result = []
    for c in clients:
        result.append({
            "id": c.id,
            "name": c.name,
            "contact_email": c.contact_email,
            "status": c.status,
            "created_at": c.created_at,
            "total_agents": len(c.agents),
            "total_assets": len(c.assets),
            "risk_score": 0, # Placeholder
            "api_key": c.client_panel_api_key, # Legacy support / UI compatibility
            "agent_api_key": c.agent_api_key,
            "client_panel_api_key": c.client_panel_api_key
        })
    return result

@router.post("/me/clients", response_model=ClientRead)
def create_client_for_partner(
    payload: ClientCreate, 
    partner: Partner = Depends(get_partner_from_api_key),
    db: Session = Depends(get_db)
):
    # Check Limits
    current_clients = db.query(Client).filter(Client.partner_id == partner.id).count()
    effective_client_limit = 1 if getattr(partner, "account_mode", "demo") == "demo" else partner.client_limit
    if current_clients >= effective_client_limit:
        msg = "Superaste el límite de la cuenta Demo (1 cliente / 1 agente)." if getattr(partner, "account_mode", "demo") == "demo" else "Has alcanzado el límite de clientes. Compra un paquete."
        raise HTTPException(status_code=403, detail=msg)

    # Generate API Keys
    new_panel_key = secrets.token_hex(8)
    new_agent_key = secrets.token_hex(16)
    
    client = Client(
        name=payload.name,
        contact_email=payload.contact_email,
        client_panel_api_key=new_panel_key,
        agent_api_key=new_agent_key,
        status="active",
        partner_id=partner.id
    )
    db.add(client)
    db.commit()
    db.refresh(client)
    return client

@router.get("/me/clients/{client_id}/api-key")
def get_client_api_key(
    client_id: str,
    partner: Partner = Depends(get_partner_from_api_key),
    db: Session = Depends(get_db)
):
    client = db.query(Client).filter(Client.id == client_id, Client.partner_id == partner.id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
        
    return {
        "api_key": client.client_panel_api_key, # Legacy
        "agent_api_key": client.agent_api_key,
        "client_panel_api_key": client.client_panel_api_key
    }

@router.get("/me/clients/{client_id}/summary")
def get_client_summary(
    client_id: str,
    partner: Partner = Depends(get_partner_from_api_key),
    db: Session = Depends(get_db)
):
    client = db.query(Client).filter(Client.id == client_id, Client.partner_id == partner.id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
        
    # Legacy Counts
    l_crit = db.query(Finding).join(Asset).filter(Asset.client_id == client.id, func.lower(Finding.severity) == "critical").count()
    l_high = db.query(Finding).join(Asset).filter(Asset.client_id == client.id, func.lower(Finding.severity) == "high").count()
    l_med = db.query(Finding).join(Asset).filter(Asset.client_id == client.id, func.lower(Finding.severity) == "medium").count()
    l_low = db.query(Finding).join(Asset).filter(Asset.client_id == client.id, func.lower(Finding.severity) == "low").count()
    
    # V2 Counts
    v_crit = db.query(NetworkVulnerability).join(NetworkAsset).filter(NetworkAsset.client_id == client.id, func.lower(NetworkVulnerability.severity) == "critical").count()
    v_high = db.query(NetworkVulnerability).join(NetworkAsset).filter(NetworkAsset.client_id == client.id, func.lower(NetworkVulnerability.severity) == "high").count()
    v_med = db.query(NetworkVulnerability).join(NetworkAsset).filter(NetworkAsset.client_id == client.id, func.lower(NetworkVulnerability.severity) == "medium").count()
    v_low = db.query(NetworkVulnerability).join(NetworkAsset).filter(NetworkAsset.client_id == client.id, func.lower(NetworkVulnerability.severity) == "info").count()

    findings_count = {
        "critical": l_crit + v_crit,
        "high": l_high + v_high,
        "medium": l_med + v_med,
        "low": l_low + v_low,
    }
    
    last_job = db.query(ScanJob).filter(ScanJob.client_id == client.id).order_by(ScanJob.created_at.desc()).first()
    
    return {
        "client": {
            "id": client.id,
            "name": client.name,
            "email": client.contact_email,
            "status": client.status,
            "created_at": client.created_at
        },
        "total_agents": len(client.agents),
        "total_assets": len(client.assets) + db.query(NetworkAsset).filter(NetworkAsset.client_id == client.id).count(), # Total approximation
        "findings_summary": findings_count,
        "last_job": {
            "id": last_job.id,
            "type": last_job.type,
            "status": last_job.status,
            "created_at": last_job.created_at
        } if last_job else None
    }

@router.get("/me/clients/{client_id}/findings", response_model=List[ClientFindingResponse])
def partner_list_client_findings(
    client_id: str,
    partner: Partner = Depends(get_partner_from_api_key),
    db: Session = Depends(get_db)
):
    client = db.query(Client).filter(Client.id == client_id, Client.partner_id == partner.id).first()
    if not client: raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    findings_list = []
    # 1. Legacy
    for f in db.query(Finding).join(Asset).filter(Finding.client_id == client.id).all():
        findings_list.append(ClientFindingResponse(
            id=f.id, asset_id=f.asset_id, asset_ip=f.asset.ip if f.asset else "Unknown",
            severity=f.severity, title=f.title, description=f.description,
            recommendation=f.recommendation, detected_at=f.detected_at
        ))
    # 2. V2
    for nv in db.query(NetworkVulnerability).join(NetworkAsset).filter(NetworkVulnerability.client_id == client.id).all():
         findings_list.append(ClientFindingResponse(
            id=nv.id, asset_id=nv.asset_id, asset_ip=nv.asset.ip if nv.asset else "Unknown",
            severity=nv.severity, title=nv.cve, description=nv.description_short,
            recommendation="Ver detalle técnico CVE", detected_at=nv.last_detected
        ))
        
    findings_list.sort(key=lambda x: x.detected_at or datetime.min.replace(tzinfo=timezone.utc), reverse=True)
    return findings_list

# ============================
# API KEYS MANAGEMENT
# ============================

@router.get("/api-keys", response_model=List[PartnerAPIKeyRead])
def list_api_keys(partner: Partner = Depends(get_partner_from_api_key), db: Session = Depends(get_db)):
    return partner.api_keys

@router.post("/api-keys", response_model=PartnerAPIKeyRead)
def create_api_key(
    payload: PartnerAPIKeyCreate,
    partner: Partner = Depends(get_partner_from_api_key),
    db: Session = Depends(get_db)
):
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

@router.delete("/api-keys/{key_id}")
def revoke_api_key(
    key_id: str,
    partner: Partner = Depends(get_partner_from_api_key),
    db: Session = Depends(get_db)
):
    key_record = db.query(PartnerAPIKey).filter(PartnerAPIKey.id == key_id, PartnerAPIKey.partner_id == partner.id).first()
    if not key_record:
        raise HTTPException(status_code=404, detail="API Key no encontrada")
        
    db.delete(key_record)
    db.commit()
    return {"status": "deleted"}

@router.delete("/me/clients/{client_id}")
def delete_client(
    client_id: str,
    partner: Partner = Depends(get_partner_from_api_key),
    db: Session = Depends(get_db)
):
    client = db.query(Client).filter(Client.id == client_id, Client.partner_id == partner.id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    # Manual Cascade Delete to avoid FK errors
    # 1. Delete Scan Results & Jobs
    # (Simplified: just delete jobs, results should cascade if configured or we delete them too)
    # Actually, let's just delete the client and let SQLAlchemy handle it if cascades are set, 
    # but since they might not be, we delete children.
    
    # Delete Scan Jobs (and their results if cascade is set on DB, otherwise we might leave orphans or error)
    db.query(ScanJob).filter(ScanJob.client_id == client.id).delete()
    
    # Delete Findings (via Assets)
    # db.query(Finding).filter(Finding.client_id == client.id).delete() # Finding has client_id
    db.query(Finding).filter(Finding.client_id == client.id).delete()

    # Delete Assets
    db.query(Asset).filter(Asset.client_id == client.id).delete()

    # Delete Agents
    db.query(Agent).filter(Agent.client_id == client.id).delete()

    # V2 CLEANUP (Prior to Client Delete)
    # -----------------------------------
    # Delete Report Snapshots Findings (via Cascade or Manual if needed)
    # SQLAlchemy usually cascades from Snapshot, but Snapshot needs deletion
    snapshots = db.query(ReportSnapshot).filter(ReportSnapshot.client_id == client.id).all()
    for s in snapshots:
        db.query(ReportSnapshotFinding).filter(ReportSnapshotFinding.snapshot_id == s.id).delete()
        db.delete(s)

    # Delete Network Vulnerabilities (Explicit)
    db.query(NetworkVulnerability).filter(NetworkVulnerability.client_id == client.id).delete()

    # Delete Network Assets (Explicit)
    db.query(NetworkAsset).filter(NetworkAsset.client_id == client.id).delete()
    
    # Delete Predictive Signals
    from app.models.domain import PredictiveSignal
    db.query(PredictiveSignal).filter(PredictiveSignal.client_id == client.id).delete()

    # Delete Threat Matches
    from app.models.domain import ClientThreatMatch
    db.query(ClientThreatMatch).filter(ClientThreatMatch.client_id == client.id).delete()

    # Delete Subscription
    if client.subscription:
        db.delete(client.subscription)

    # Delete Client
    db.delete(client)
    db.commit()
    
    return {"status": "deleted", "id": client_id}

# ============================
# REMOTE SOC ACTIONS (PARTNER)
# ============================

@router.post("/me/clients/{client_id}/scan", response_model=ScanJobResponse)
def partner_run_scan(
    client_id: str,
    payload: PartnerScanRequest,
    partner: Partner = Depends(get_partner_from_api_key),
    db: Session = Depends(get_db)
):
    # 1. Validate Ownership
    client = db.query(Client).filter(Client.id == client_id, Client.partner_id == partner.id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    # 3. Determine Agent Logic (Smart Assignment)
    # Priority:
    # 1. Specified agent (must exist and be owned by client)
    # 2. Online agent (any)
    # 3. Any agent (fallback, left unassigned for claim)
    
    agent = None
    target_agent_id = None
    
    if payload.agent_id:
        agent = db.query(Agent).filter(Agent.id == payload.agent_id, Agent.client_id == client.id).first()
        if not agent:
            raise HTTPException(status_code=404, detail="Agente especificado no encontrado o no pertenece al cliente")
        target_agent_id = agent.id
    else:
        # Try to find an ONLINE agent first
        online_agent = db.query(Agent).filter(Agent.client_id == client.id, Agent.status == "online").first()
        if online_agent:
            target_agent_id = online_agent.id
            agent = online_agent
        else:
            # Check if ANY agent exists at all
            any_agent = db.query(Agent).filter(Agent.client_id == client.id).first()
            if not any_agent:
                raise HTTPException(status_code=400, detail="No hay agentes registrados para este cliente. Instale un agente primero.")
            # We leave target_agent_id as None. Any agent coming online will claim it via Heartbeat.
            agent = any_agent # Just for target CIDR fallback if needed

    # 4. Create Job
    new_job = ScanJob(
        client_id=client.id,
        agent_id=target_agent_id, # Can be None now
        type=payload.type,
        target=payload.target if payload.target else (agent.primary_cidr if agent else "127.0.0.1"),
        status="pending",
        params={"source": "partner_console", "partner_id": partner.id}
    )
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    return new_job

@router.post("/me/clients/{client_id}/agents/{agent_id}/action")
def partner_agent_action(
    client_id: str,
    agent_id: str,
    payload: PartnerAgentActionRequest,
    partner: Partner = Depends(get_partner_from_api_key),
    db: Session = Depends(get_db)
):
    # 1. Validate Ownership
    client = db.query(Client).filter(Client.id == client_id, Client.partner_id == partner.id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
        
    agent = db.query(Agent).filter(Agent.id == agent_id, Agent.client_id == client.id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agente no encontrado")

    # 2. Create Action Job (Special Job Type)
    job_type = f"command:{payload.action}"
    
    new_job = ScanJob(
        client_id=client.id,
        agent_id=agent.id,
        type=job_type,
        target="localhost",
        status="pending",
        params={"source": "partner_console", "action": payload.action}
    )
    db.add(new_job)
    db.commit()
    
    return {"status": "queued", "job_id": new_job.id, "action": payload.action}

@router.get("/me/agents")
def list_my_agents(partner: Partner = Depends(get_partner_from_api_key), db: Session = Depends(get_db)):
    agents = db.query(Agent).join(Client).filter(Client.partner_id == partner.id).all()
    res = []
    for a in agents:
        # Compute real-time status based on last_seen_at
        real_status = compute_agent_online_status(a)
        res.append({
            "id": a.id, "hostname": a.hostname, "client_name": a.client.name, 
            "status": real_status,  # Use computed status instead of stored
            "version": a.version, "capabilities": a.capabilities, 
            "last_seen_at": a.last_seen_at
        })
    return res

class PartnerMassUpdateRequest(BaseModel):
    version: str = "latest"

@router.post("/me/agents/update")
def trigger_partner_mass_update(
    payload: PartnerMassUpdateRequest,
    partner: Partner = Depends(get_partner_from_api_key), 
    db: Session = Depends(get_db)
):
    latest = db.query(AgentVersion).filter(AgentVersion.platform == "windows", AgentVersion.tier == "stable").order_by(desc(AgentVersion.release_date)).first()
    if not latest: raise HTTPException(404, "No updates available")
    
    # Select Agents of this Partner (ONLINE only)
    agents = db.query(Agent).join(Client).filter(Client.partner_id == partner.id, Agent.status == "online").all()
    
    count = 0
    for a in agents:
        if a.version == latest.version: continue
        # Check existing job
        job = db.query(ScanJob).filter(ScanJob.agent_id==a.id, ScanJob.type=="self_update", ScanJob.status.in_(['pending','running'])).first()
        if job: continue
        
        new_job = ScanJob(client_id=a.client_id, agent_id=a.id, type="self_update", target="local", status="pending", params={"version": latest.version, "url":latest.download_url, "sha256":latest.checksum_sha256})
        db.add(new_job)
        count += 1
    db.commit()
    return {"queued": count, "version": latest.version}

@router.get("/me/clients/{client_id}/jobs", response_model=List[ScanJobResponse])
def partner_list_client_jobs(
    client_id: str,
    limit: int = 20,
    partner: Partner = Depends(get_partner_from_api_key),
    db: Session = Depends(get_db)
):
    client = db.query(Client).filter(Client.id == client_id, Client.partner_id == partner.id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
        
    jobs = db.query(ScanJob).filter(ScanJob.client_id == client.id).order_by(ScanJob.created_at.desc()).limit(limit).all()
    return jobs

# Legacy Report / ReportSnapshot Logic follows

# ... [Keep imports and existing code up to line 479] ...

@router.get("/me/clients/{client_id}/reports", response_model=List[ReportResponse])
def partner_list_client_reports(
    client_id: str,
    partner: Partner = Depends(get_partner_from_api_key),
    db: Session = Depends(get_db)
):
    client = db.query(Client).filter(Client.id == client_id, Client.partner_id == partner.id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
        
    reports = (
        db.query(ReportSnapshot)
        .filter(ReportSnapshot.client_id == client.id)
        .order_by(desc(ReportSnapshot.created_at))
        .all()
    )

    result: List[ReportResponse] = []
    for r in reports:
        download_url = f"/api/partners/me/clients/{client_id}/reports/{r.id}/download"
        summary_text = f"Assets: {r.assets_count} | Findings: {r.findings_count} | Score: {r.risk_score}"
        
        result.append(ReportResponse(
            id=r.id,
            client_id=client.id,
            client_name=client.name,
            type=r.kind,
            generated_at=r.created_at,
            download_url=download_url,
            title=f"Reporte {r.kind}",
            status=r.status,
            summary=summary_text,
            assets_count=r.assets_count,
            findings_count=r.findings_count,
            risk_score=r.risk_score
        ))
    return result


    # Create Snapshot Record
    snapshot_id = str(uuid.uuid4())
    snapshot = ReportSnapshot(
        id=snapshot_id,
        client_id=client.id,
        job_id=scan_job.id if scan_job else None,
        kind=payload.type,
        status="generating",
        assets_count=total_assets,
        findings_count=len(all_findings),
        risk_score=risk_score,
        filter_date_from=start_time,
        created_at=datetime.utcnow()
    )
    db.add(snapshot)
    
    # Process for Snapshot Findings (Persistence)
    snapshot_findings_objects = []
    
    for item in all_findings:
        key = (item["title"], item["severity"], item["cve"])
        
        sf = ReportSnapshotFinding(
            id=str(uuid.uuid4()),
            snapshot_id=snapshot_id,
            asset_id=item["asset_id"],
            title=item["title"],
            severity=item["severity"],
            cve=item["cve"],
            description=item["description"],
            recommendation=item["recommendation"]
        )
        snapshot_findings_objects.append(sf)

        if key not in grouped_findings:
            grouped_findings[key] = {
                "title": item["title"], "severity": item["severity"], "cve": item["cve"],
                "description": item["description"] or "Sin descripción",
                "recommendation": item["recommendation"],
                "assets": []
            }
        
        asset_txt = f"{item['ip']} ({item['hostname'] or ''})"
        if asset_txt not in grouped_findings[key]["assets"]:
            grouped_findings[key]["assets"].append(asset_txt)
            
    db.add_all(snapshot_findings_objects)
    db.commit() # Commit IDs
    
    findings_data = []
    for k, item in grouped_findings.items():
        assets_str = ", ".join(item["assets"][:5])
        if len(item["assets"]) > 5: assets_str += f" y {len(item['assets'])-5} más"
        findings_data.append({
            "severity": item["severity"].upper(), "title": item["title"],
            "asset_ip": assets_str, "description": item["description"], "recommendation": item["recommendation"]
        })
        
    if payload.type == "executive": findings_data = findings_data[:10]

    # 5. Generate PDF
    generator = ReportGenerator()
    try:
        filename = generator.generate_pdf_report(client.name, stats, findings_data, "es", payload.type)
        status_report = "ready"
    except Exception as e:
        print(f"PDF Error: {e}")
        filename = f"error_{uuid.uuid4()}.pdf" # Fallback
        status_report = "error"

    # 6. Update Snapshot
    snapshot.pdf_path = filename
    snapshot.status = status_report
    snapshot.pdf_url = f"/api/partners/me/clients/{client_id}/reports/{snapshot.id}/download"
    db.commit()
    db.refresh(snapshot)

    return ReportResponse(
        id=snapshot.id, client_id=client.id, client_name=client.name, type=snapshot.kind,
        generated_at=snapshot.created_at, download_url=snapshot.pdf_url,
        title=f"Reporte {snapshot.kind}", status=snapshot.status,
        summary=f"Assets: {total_assets} | Risk: {risk_score}",
        assets_count=total_assets,
        findings_count=len(all_findings),
        risk_score=risk_score
    )

@router.get("/me/clients/{client_id}/jobs/{job_id}/result")
def partner_get_job_result(
    client_id: str,
    job_id: str,
    partner: Partner = Depends(get_partner_from_api_key),
    db: Session = Depends(get_db)
):
    """
    Returns raw data (data field) of a completed scan job.
    Uses AgentJobResult logic or fallback to ScanJob params if empty (for debug).
    """
    client = db.query(Client).filter(Client.id == client_id, Client.partner_id == partner.id).first()
    if not client: raise HTTPException(404, "Client not found")

    job = db.query(ScanJob).filter(ScanJob.id == job_id, ScanJob.client_id == client.id).first()
    if not job: raise HTTPException(404, "Job not found")

    # In a real scenario, big raw data might be in S3 or separate table.
    # For now (MVP), we assume data *might* be in job params (if stored) or we mock it for demonstration if missing
    # Or ideally, we should check `AgentJobResult` table if implemented? 
    # Let's check Contracts... Yes, `AgentJobResult`. DB model? Not imported in this file.
    
    # Let's return what we have on the specific job record + params.
    # If we had a `scan_results` table, we'd query that.
    
    # MOCK/SIMULATION for MVP if NULL:
    # If job is X-RAY, return the NetworkAssets detected by it?
    
    return {
        "status": "ok",
        "job_id": job.id,
        "type": job.type,
        "data": job.params or { "info": "Raw data not persisted in this version." }
    }


@router.get("/me/clients/{client_id}/reports/{report_id}/download")
def partner_download_report(
    client_id: str,
    report_id: str,
    partner: Partner = Depends(get_partner_from_api_key),
    db: Session = Depends(get_db)
):
    client = db.query(Client).filter(Client.id == client_id, Client.partner_id == partner.id).first()
    if not client: raise HTTPException(status_code=404, detail="Cliente no encontrado")

    snapshot = db.query(ReportSnapshot).filter(ReportSnapshot.id == report_id, ReportSnapshot.client_id == client.id).first()
    if not snapshot or not snapshot.pdf_path:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")

    filepath = os.path.join("/tmp/reports", os.path.basename(snapshot.pdf_path))
    if not os.path.exists(filepath):
        # Check alternate location if generator output dir is different
        raise HTTPException(status_code=404, detail="Archivo de reporte no encontrado en disco")

    return FileResponse(filepath, media_type="application/pdf", filename=f"Report_{client.name}_{snapshot.kind}.pdf")


@router.post("/me/clients/{client_id}/reports", response_model=ReportResponse)
def partner_generate_report(
    client_id: str,
    payload: PartnerReportRequest,
    partner: Partner = Depends(get_partner_from_api_key),
    db: Session = Depends(get_db)
):
    client = db.query(Client).filter(Client.id == client_id, Client.partner_id == partner.id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    # Reuse robust logic pattern from reports.py (Snapshot Generation)
    
    # 1. Resolve Job (Specific or Latest Done)
    scan_job = None
    if payload.scan_id:
        scan_job = db.query(ScanJob).filter(ScanJob.id == payload.scan_id, ScanJob.client_id == client.id).first()
        if not scan_job: raise HTTPException(404, "Specifed Scan Job not found")
    else:
        scan_job = db.query(ScanJob).filter(
            ScanJob.client_id == client_id, 
            ScanJob.status == "done"
        ).order_by(ScanJob.finished_at.desc()).first()
    
    # 1.1 Check Exists
    if not payload.force and scan_job:
        existing = db.query(ReportSnapshot).filter(
            ReportSnapshot.client_id == client_id,
            ReportSnapshot.job_id == scan_job.id, # Link strictly to job
            ReportSnapshot.kind == payload.type
        ).first()
        if existing and existing.status == "ready":
             download_url = f"/api/partners/me/clients/{client_id}/reports/{existing.id}/download"
             return ReportResponse(
                id=existing.id, client_id=client.id, client_name=client.name, type=existing.kind,
                generated_at=existing.created_at, download_url=download_url,
                title=f"Reporte {existing.kind}", status=existing.status,
                summary=f"Assets: {existing.assets_count} | Findings: {existing.findings_count}",
                assets_count=existing.assets_count,
                findings_count=existing.findings_count,
                risk_score=existing.risk_score
             )

    # 2. Fetch Data (V2 + Legacy)
    # If explicit scan_id, use its time as retrieval point, OR assume current state reflects it?
    # Logic: "Snapshot" means taking state NOW. But if user selected OLD scan, they might expect OLD data?
    # Snapshots are immutable. If they generate it NOW for an OLD job, it technically is a SNAPSHOT of NOW linked to OLD job.
    # Ideally we use `Time Travel` query `detected_at <= scan_job.finished_at`.
    # For MVP we keep `last_seen >= window` but ensure we respect job linkage.
    
    start_time = datetime.utcnow() - timedelta(days=365)
    if scan_job:
        base_time = scan_job.started_at or scan_job.created_at
        if base_time: start_time = base_time - timedelta(hours=24)
            
    scan_assets = db.query(NetworkAsset).filter(NetworkAsset.client_id == client.id, NetworkAsset.last_seen >= start_time).all()
    
    # 2.1 X-RAY (V2)
    v2_vulns = db.query(NetworkVulnerability).join(NetworkAsset).filter(
        NetworkAsset.client_id == client.id, 
        NetworkAsset.last_seen >= start_time
    ).all()
    
    # 2.2 Legacy Findings
    legacy_findings = db.query(Finding).join(Asset).filter(
        Finding.client_id == client.id
    ).all()

    # Unified Structure
    all_findings = []
    
    for v in v2_vulns:
        all_findings.append({
            "asset_id": v.asset_id,
            "ip": v.asset.ip,
            "hostname": v.asset.hostname,
            "title": v.cve, # V2 convention
            "severity": v.severity,
            "cve": v.cve,
            "description": v.description_short,
            "recommendation": "Ver detalle técnico (CVE)."
        })
        
    for f in legacy_findings:
        all_findings.append({
            "asset_id": f.asset_id,
            "ip": f.asset.ip,
            "hostname": f.asset.hostname,
            "title": f.title,
            "severity": f.severity,
            "cve": None,
            "description": f.description,
            "recommendation": f.recommendation
        })

    # 3. Stats
    total_assets = len(scan_assets) # Keep consistent with client logic
    critical = len([x for x in all_findings if x["severity"].lower() == "critical"])
    high = len([x for x in all_findings if x["severity"].lower() == "high"])
    medium = len([x for x in all_findings if x["severity"].lower() == "medium"])
    risk_score = max(0, 100 - ((critical * 10) + (high * 5) + (medium * 1)))
    
    stats = {
        "total_assets": total_assets, "active_agents": len(client.agents),
        "critical_findings": critical, "high_findings": high, "medium_findings": medium,
        "risk_score": risk_score,
        "scan_id": scan_job.id if scan_job else "N/A",
        "scan_date": scan_job.finished_at.strftime("%Y-%m-%d") if scan_job and scan_job.finished_at else "Unknown"
    }

    # 4. Group Findings & Persistence
    grouped_findings = {}
    
    # Create Snapshot Record
    snapshot_id = str(uuid.uuid4())
    snapshot = ReportSnapshot(
        id=snapshot_id,
        client_id=client.id,
        job_id=scan_job.id if scan_job else None,
        kind=payload.type,
        status="generating",
        assets_count=total_assets,
        findings_count=len(all_findings),
        risk_score=risk_score,
        filter_date_from=start_time,
        created_at=datetime.utcnow()
    )
    db.add(snapshot)
    
    # Process for Snapshot Findings (Persistence)
    snapshot_findings_objects = []
    
    for item in all_findings:
        key = (item["title"], item["severity"], item["cve"])
        
        sf = ReportSnapshotFinding(
            id=str(uuid.uuid4()),
            snapshot_id=snapshot_id,
            asset_id=item["asset_id"],
            title=item["title"],
            severity=item["severity"],
            cve=item["cve"],
            description=item["description"],
            recommendation=item["recommendation"]
        )
        snapshot_findings_objects.append(sf)

        if key not in grouped_findings:
            grouped_findings[key] = {
                "title": item["title"], "severity": item["severity"], "cve": item["cve"],
                "description": item["description"] or "Sin descripción",
                "recommendation": item["recommendation"],
                "assets": []
            }
        
        asset_txt = f"{item['ip']} ({item['hostname'] or ''})"
        if asset_txt not in grouped_findings[key]["assets"]:
            grouped_findings[key]["assets"].append(asset_txt)
            
    db.add_all(snapshot_findings_objects)
    db.commit() # Commit IDs
    
    findings_data = []
    for k, item in grouped_findings.items():
        assets_str = ", ".join(item["assets"][:5])
        if len(item["assets"]) > 5: assets_str += f" y {len(item['assets'])-5} más"
        findings_data.append({
            "severity": item["severity"].upper(), "title": item["title"],
            "asset_ip": assets_str, "description": item["description"], "recommendation": item["recommendation"]
        })
        
    if payload.type == "executive": findings_data = findings_data[:10]

    # 5. Generate PDF
    generator = ReportGenerator()
    try:
        filename = generator.generate_pdf_report(client.name, stats, findings_data, "es", payload.type)
        status_report = "ready"
    except Exception as e:
        print(f"PDF Error: {e}")
        filename = f"error_{uuid.uuid4()}.pdf" # Fallback
        status_report = "error"

    # 6. Update Snapshot
    snapshot.pdf_path = filename
    snapshot.status = status_report
    snapshot.pdf_url = f"/api/partners/me/clients/{client_id}/reports/{snapshot.id}/download"
    db.commit()
    db.refresh(snapshot)

    return ReportResponse(
        id=snapshot.id, client_id=client.id, client_name=client.name, type=snapshot.kind,
        generated_at=snapshot.created_at, download_url=snapshot.pdf_url,
        title=f"Reporte {snapshot.kind}", status=snapshot.status,
        summary=f"Assets: {total_assets} | Risk: {risk_score}",
        assets_count=total_assets,
        findings_count=len(all_findings),
        risk_score=risk_score
    )


@router.get("/me/clients/{client_id}/reports/{report_id}/download")
def partner_download_report(
    client_id: str,
    report_id: str,
    partner: Partner = Depends(get_partner_from_api_key),
    db: Session = Depends(get_db)
):
    client = db.query(Client).filter(Client.id == client_id, Client.partner_id == partner.id).first()
    if not client: raise HTTPException(status_code=404, detail="Cliente no encontrado")

    snapshot = db.query(ReportSnapshot).filter(ReportSnapshot.id == report_id, ReportSnapshot.client_id == client.id).first()
    if not snapshot or not snapshot.pdf_path:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")

    filepath = os.path.join("/tmp/reports", os.path.basename(snapshot.pdf_path))
    if not os.path.exists(filepath):
        # Check alternate location if generator output dir is different
        raise HTTPException(status_code=404, detail="Archivo de reporte no encontrado en disco")

    return FileResponse(filepath, media_type="application/pdf", filename=f"Report_{client.name}_{snapshot.kind}.pdf")

