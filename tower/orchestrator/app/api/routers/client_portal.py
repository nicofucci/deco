from typing import List, Optional
from datetime import datetime, timezone
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_client_from_panel_key
from app.models.domain import Asset, Finding, ScanJob, ScanResult, Client, NetworkAsset, NetworkVulnerability
from app.schemas.contracts import (
    ClientAssetResponse,
    ClientFindingResponse,
    ClientJobResponse,
    ReportSummaryResponse,
)
from app.services.reports import generate_client_report

router = APIRouter()

logger = logging.getLogger("DecoOrchestrator.ClientPortal")
logger.setLevel(logging.INFO)
if not logger.handlers:
    import sys

    handler = logging.StreamHandler(sys.stdout)
    logger.addHandler(handler)


def _extract_ports(raw_data: dict, target_ip: str | None = None) -> List[int]:
    """
    Normaliza el listado de puertos abiertos desde el raw_data del resultado.
    Si hay estructura hosts, intenta asociar por IP.
    """
    if not isinstance(raw_data, dict):
        return []
    if target_ip and isinstance(raw_data.get("hosts"), list):
        for host in raw_data["hosts"]:
            if isinstance(host, dict) and host.get("ip") == target_ip:
                ports = host.get("open_ports") or host.get("ports")
                if ports:
                    try:
                        return sorted({int(p) for p in ports})
                    except Exception:
                        pass
    ports = raw_data.get("open_ports") or raw_data.get("ports")
    if not ports and isinstance(raw_data.get("data"), dict):
        ports = raw_data["data"].get("open_ports") or raw_data["data"].get("ports")
    if not ports:
        return []
    try:
        return sorted({int(p) for p in ports})
    except Exception:
        return []


@router.get("/assets", response_model=List[ClientAssetResponse])
def list_client_assets(
    db: Session = Depends(get_db),
    client: Client = Depends(get_client_from_panel_key),
):
    """
    Devuelve los activos del cliente autenticado con puertos abiertos y última fecha de escaneo.
    Combina Asset (Legacy) y NetworkAsset (X-RAY).
    """
    # 1. Legacy Assets
    assets = (
        db.query(Asset)
        .filter(Asset.client_id == client.id)
        .all()
    )
    
    # 2. X-RAY Assets
    net_assets = (
        db.query(NetworkAsset)
        .filter(NetworkAsset.client_id == client.id)
        .all()
    )

    response: List[ClientAssetResponse] = []
    
    # Process Legacy
    for asset in assets:
        latest_result = (
            db.query(ScanResult)
            .join(ScanJob, ScanResult.scan_job_id == ScanJob.id)
            .filter(ScanJob.client_id == client.id)
            .order_by(ScanResult.created_at.desc())
            .first()
        )
        open_ports: List[int] = []
        last_scan_at = None
        if latest_result:
            open_ports = _extract_ports(latest_result.raw_data, asset.ip)
            last_scan_at = latest_result.created_at

        response.append(
            ClientAssetResponse(
                id=asset.id,
                ip=asset.ip,
                hostname=asset.hostname,
                client_name=None,
                open_ports=open_ports,
                last_scan_at=last_scan_at,
            )
        )
        
    # Process X-RAY
    for net_asset in net_assets:
        # Check duplication by IP? For now append all to ensure visibility.
        # Ideally user wants unified list, but let's prioritize showing DATA.
        response.append(
            ClientAssetResponse(
                id=net_asset.id,
                ip=net_asset.ip,
                hostname=net_asset.hostname,
                client_name=None,
                open_ports=net_asset.open_ports or [],
                last_scan_at=net_asset.last_seen,
            )
        )
            
    # Deduplicate by IP optionally? 
    # For now, sorting by date makes sense.
    response.sort(key=lambda x: x.last_scan_at or datetime.min.replace(tzinfo=timezone.utc), reverse=True)
    return response


@router.get("/findings", response_model=List[ClientFindingResponse])
def list_client_findings(
    asset_id: Optional[str] = None,
    db: Session = Depends(get_db),
    client: Client = Depends(get_client_from_panel_key),
):
    """
    Devuelve los hallazgos del cliente con el IP del activo.
    Combina Finding (Legacy) y NetworkVulnerability (X-RAY).
    """
    findings_list = []
    
    # 1. Legacy Findings
    query = (
        db.query(Finding)
        .join(Asset, Finding.asset_id == Asset.id)
        .filter(Finding.client_id == client.id)
    )
    if asset_id:
        query = query.filter(Finding.asset_id == asset_id)
        
    for f in query.all():
        findings_list.append(
            ClientFindingResponse(
                id=f.id,
                asset_id=f.asset_id,
                asset_ip=f.asset.ip if f.asset else "Unknown",
                severity=f.severity,
                title=f.title,
                description=f.description,
                recommendation=f.recommendation,
                detected_at=f.detected_at,
            )
        )

    # 2. X-RAY Network Vulnerabilities
    nv_query = (
        db.query(NetworkVulnerability)
        .join(NetworkAsset, NetworkVulnerability.asset_id == NetworkAsset.id)
        .filter(NetworkVulnerability.client_id == client.id)
    )
    if asset_id:
        nv_query = nv_query.filter(NetworkVulnerability.asset_id == asset_id)
        
    for nv in nv_query.all():
        findings_list.append(
            ClientFindingResponse(
                id=nv.id,
                asset_id=nv.asset_id,
                asset_ip=nv.asset.ip if nv.asset else "Unknown",
                severity=nv.severity,
                title=nv.cve, # Use CVE as title
                description=nv.description_short or "Detectado por X-RAY",
                recommendation="Ver detalle técnico CVE",
                detected_at=nv.last_detected,
            )
        )
        
    # Sort unified list
    findings_list.sort(key=lambda x: x.detected_at or datetime.min.replace(tzinfo=timezone.utc), reverse=True)
    
    return findings_list


@router.get("/jobs", response_model=List[ClientJobResponse])
def list_client_jobs(
    db: Session = Depends(get_db),
    client: Client = Depends(get_client_from_panel_key),
):
    """
    Lista los jobs de escaneo del cliente, incluyendo estado temporal.
    """
    jobs = (
        db.query(ScanJob)
        .filter(ScanJob.client_id == client.id)
        .order_by(ScanJob.created_at.desc())
        .all()
    )
    return [
        ClientJobResponse(
            id=j.id,
            type=j.type,
            target=j.target,
            status=j.status,
            created_at=j.created_at,
            started_at=j.started_at,
            finished_at=j.finished_at,
        )
        for j in jobs
    ]


@router.post("/reports/summary", response_model=ReportSummaryResponse)
def generate_report_summary(
    format: str = "html",
    db: Session = Depends(get_db),
    client: Client = Depends(get_client_from_panel_key),
):
    """
    Genera un informe ligero para el cliente autenticado.
    """
    report = generate_client_report(db, client, format=format)
    logger.info(f"[REPORT] Informe generado para cliente={client.id} formato={report['format']}")
    return report


@router.get("/overview")
def get_client_overview(
    db: Session = Depends(get_db),
    client: Client = Depends(get_client_from_panel_key),
):
    """
    Resumen del dashboard del cliente.
    """
    from app.models.domain import Agent
    
    total_agents = db.query(Agent).filter(Agent.client_id == client.id).count()
    active_agents = db.query(Agent).filter(Agent.client_id == client.id, Agent.status == "online").count()
    
    findings_critical = db.query(Finding).filter(Finding.client_id == client.id, Finding.severity == "critical").count()
    findings_high = db.query(Finding).filter(Finding.client_id == client.id, Finding.severity == "high").count()
    findings_medium = db.query(Finding).filter(Finding.client_id == client.id, Finding.severity == "medium").count()
    
    last_scan = db.query(ScanJob).filter(ScanJob.client_id == client.id, ScanJob.status == "completed").order_by(ScanJob.finished_at.desc()).first()
    
    return {
        "agents_total": total_agents,
        "agents_active": active_agents,
        "findings_critical": findings_critical,
        "findings_high": findings_high,
        "findings_medium": findings_medium,
        "last_scan_at": last_scan.finished_at if last_scan else None
    }


@router.get("/agents")
def list_client_agents(
    db: Session = Depends(get_db),
    client: Client = Depends(get_client_from_panel_key),
):
    """
    Lista agentes del cliente.
    """
    from app.models.domain import Agent
    
    agents = db.query(Agent).filter(Agent.client_id == client.id).order_by(Agent.last_seen_at.desc()).all()
    
    return [
        {
            "id": a.id,
            "hostname": a.hostname,
            "status": a.status,
            "last_seen_at": a.last_seen_at,
            "ip": a.local_ip or a.ip,
            "os": a.os or "Unknown"
        }
        for a in agents
    ]


@router.get("/reports")
def list_client_reports(
    db: Session = Depends(get_db),
    client: Client = Depends(get_client_from_panel_key),
):
    """
    Lista reportes PDF disponibles para el cliente.
    """
    # TODO: Implement actual file listing from storage/DB
    # For now return empty list or mock
    return []
