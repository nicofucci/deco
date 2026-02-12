from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query, Header
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.api.deps import get_db, verify_master_key
from app.services.reports import ReportGenerator
from app.models.domain import Client, NetworkAsset, NetworkVulnerability, ScanJob, ReportSnapshot, ReportSnapshotFinding, Report, Asset, Finding
import os
import uuid
import shutil
from datetime import datetime, timedelta, timezone

router = APIRouter()
report_gen = ReportGenerator()


@router.get("/clients/{client_id}/reports")
def list_reports(
    client_id: str,
    limit: int = 50,
    kind: str = None,
    db: Session = Depends(get_db),
):
    # 1. New Snapshots
    query = db.query(ReportSnapshot).filter(ReportSnapshot.client_id == client_id)
    if kind:
        query = query.filter(ReportSnapshot.kind == kind)
    snapshots = query.order_by(ReportSnapshot.created_at.desc()).limit(limit).all()

    # 2. Legacy Reports
    legacy_query = db.query(Report).filter(Report.client_id == client_id)
    if kind:
        # Legacy uses 'type' column
        legacy_query = legacy_query.filter(Report.type == kind)
    legacy_reports = legacy_query.order_by(Report.created_at.desc()).limit(limit).all()

    # 3. Merge results
    results = []
    
    for s in snapshots:
        results.append({
            "id": s.id,
            "job_id": s.job_id,
            "kind": s.kind,
            "created_at": s.created_at,
            "assets_count": s.assets_count,
            "findings_count": s.findings_count,
            "risk_score": s.risk_score,
            "status": s.status,
            "pdf_url": s.pdf_url or (f"/api/reports/download/{s.pdf_path}" if s.pdf_path else None),
            "is_legacy": False
        })
        
    for r in legacy_reports:
        # Check if this legacy report is already covered by a snapshot (unlikely if user says they are missing)
        # Just map fields.
        results.append({
            "id": r.id,
            "job_id": r.job_id,
            "kind": r.type, # Map type -> kind
            "created_at": r.created_at,
            "assets_count": 0, # Unknown
            "findings_count": 0, # Unknown
            "risk_score": 0, # Unknown
            "status": r.status or "completed",
            "pdf_url": f"/api/reports/download/{os.path.basename(r.file_path)}" if r.file_path else None,
            "is_legacy": True
        })
        
    # Sort combined list by date desc
    results.sort(key=lambda x: x["created_at"] or datetime.min.replace(tzinfo=timezone.utc), reverse=True)
    
    return results[:limit]

@router.post("/generate/{client_id}")
def generate_report(
    client_id: str,
    scan_id: str = None, # Optional context
    type: str = "executive", # Mapped to 'kind'
    lang: str = "es",
    force: bool = False,
    db: Session = Depends(get_db),
    # auth logic handled inside or via custom dep
    x_admin_key: str = Header(None, alias="X-Admin-Master-Key"),
    x_client_key: str = Header(None, alias="X-Client-API-Key")
):
    # 0. Auth Check (Hybrid: Admin or Client Owner)
    is_admin = False
    if x_admin_key:
        from app.api.deps import ADMIN_MASTER_KEY
        if x_admin_key == ADMIN_MASTER_KEY:
            is_admin = True
    
    auth_client = None
    if not is_admin:
        if not x_client_key:
             raise HTTPException(status_code=401, detail="Missing Authentication (Admin Key or Client Key)")
        
        # Verify Client Key
        auth_client = db.query(Client).filter(Client.agent_api_key == x_client_key).first()
        if not auth_client:
             auth_client = db.query(Client).filter(Client.client_panel_api_key == x_client_key).first()
        
        if not auth_client:
             raise HTTPException(status_code=403, detail="Invalid Client Key")
             
        if auth_client.id != client_id:
             raise HTTPException(status_code=403, detail="Client Key does not match target Client ID")

    # If we are admin, fetch the target client
    if is_admin:
        client = db.query(Client).filter(Client.id == client_id).first()
    else:
        client = auth_client

    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    # 1. Resolve Scan Context
    scan_job = None
    if scan_id and scan_id != "latest":
        scan_job = db.query(ScanJob).filter(ScanJob.id == scan_id, ScanJob.client_id == client_id).first()
        if not scan_job:
            raise HTTPException(status_code=404, detail="Scan Job not found")
    else:
        # Auto-select latest DONE scan
        scan_job = db.query(ScanJob).filter(
            ScanJob.client_id == client_id, 
            ScanJob.status == "done"
        ).order_by(ScanJob.finished_at.desc()).first()
    
    if not scan_job:
        raise HTTPException(status_code=400, detail="No completed scans found for this client. Cannot generate report without real data.")

    # 1.1 Check for Existing Snapshot (Idempotency)
    if not force:
        existing = db.query(ReportSnapshot).filter(
            ReportSnapshot.client_id == client_id,
            ReportSnapshot.job_id == scan_job.id,
            ReportSnapshot.kind == type
        ).first()
        
        if existing and existing.status == "ready":
             return {
                "id": existing.id,
                "status": "ready",
                "download_url": existing.pdf_url or f"/api/reports/download/{existing.pdf_path}",
                "lang": lang,
                "scan_context": scan_job.id,
                "assets_included": existing.assets_count
            }

    # 2. Fetch Assets (Context: Last Seen >= Scan Start)
    base_time = scan_job.started_at or scan_job.created_at
    if base_time:
         start_time = base_time - timedelta(hours=24)
    else:
         start_time = datetime.utcnow() - timedelta(days=365)
    
    scan_assets = db.query(NetworkAsset).filter(
        NetworkAsset.client_id == client_id,
        NetworkAsset.last_seen >= start_time 
    ).all()
    
    # Fail-Safe: Integrity Check
    if not scan_assets:
         raise HTTPException(status_code=400, detail=f"Scan {scan_job.id} has NO assets. Refusing to generate empty/fake report.")

    # 3. Fetch Vulnerabilities (V2 + Legacy)
    
    # 3.1 X-RAY (V2)
    v2_vulns = db.query(NetworkVulnerability).join(NetworkAsset).filter(
        NetworkAsset.client_id == client_id,
        NetworkAsset.last_seen >= start_time
    ).all()
    
    # 3.2 Legacy Findings
    legacy_findings = db.query(Finding).join(Asset).filter(
        Finding.client_id == client_id
    ).all()
    
    # Unified Structure
    all_findings = []
    
    for v in v2_vulns:
        all_findings.append({
            "obj": v,
            "source": "v2",
            "asset_id": v.asset_id,
            "ip": v.asset.ip,
            "hostname": v.asset.hostname,
            "title": v.cve, # Use CVE as title for V2 per user preference in V2 context
            "severity": v.severity,
            "cve": v.cve,
            "description": v.description_short,
            "recommendation": "Ver detalle técnico (CVE)."
        })
        
    for f in legacy_findings:
        all_findings.append({
            "obj": f,
            "source": "legacy",
            "asset_id": f.asset_id,
            "ip": f.asset.ip,
            "hostname": f.asset.hostname,
            "title": f.title,
            "severity": f.severity,
            "cve": None,
            "description": f.description,
            "recommendation": f.recommendation
        })

    # 3.3 Calculate Real Stats
    total_assets = len(scan_assets) # Only counting NetworkAssets here? 
    # Legacy assets might be separate. But report context is usually "This Scan". 
    # If we include Legacy Findings, we imply coverage of legacy assets.
    # We should probably count unique IPs from both asset lists?
    # For now, keep total_assets as scan coverage + active agents?
    # Stats dict uses 'total_assets'.
    
    critical_count = len([x for x in all_findings if x["severity"].lower() == "critical"])
    high_count = len([x for x in all_findings if x["severity"].lower() == "high"])
    medium_count = len([x for x in all_findings if x["severity"].lower() == "medium"])
    
    risk_deduction = (critical_count * 10) + (high_count * 5) + (medium_count * 1)
    risk_score = max(0, 100 - risk_deduction)
    
    stats = {
        "total_assets": total_assets,
        "active_agents": len(client.agents),
        "critical_findings": critical_count,
        "high_findings": high_count,
        "medium_findings": medium_count,
        "risk_score": risk_score,
        "scan_id": scan_job.id,
        "scan_date": scan_job.finished_at.strftime("%Y-%m-%d %H:%M:%S") if scan_job.finished_at else "Unknown"
    }

    # 4. Prepare Findings Data (Deduplication & Grouping)
    grouped_findings = {}
    
    # Create Snapshot Record
    snapshot_id = str(uuid.uuid4())
    snapshot = ReportSnapshot(
        id=snapshot_id,
        client_id=client_id,
        job_id=scan_job.id,
        kind=type,
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
        # Group logic for PDF
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

        # Grouping for PDF Generation
        if key not in grouped_findings:
            grouped_findings[key] = {
                "title": item["title"],
                "severity": item["severity"],
                "cve": item["cve"],
                "description": item["description"] or "Sin descripción",
                "recommendation": item["recommendation"],
                "assets": []
            }
        
        asset_info = f"{item['ip']} ({item['hostname'] or 'Unknown'})"
        if asset_info not in grouped_findings[key]["assets"]:
            grouped_findings[key]["assets"].append(asset_info)
            
    db.add_all(snapshot_findings_objects)
    db.commit() # Commit so we have IDs and saved state
    
    # 5. Generate PDF from Grouped Data
    findings_data = []
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
    sorted_keys = sorted(grouped_findings.keys(), key=lambda x: severity_order.get(x[1].lower(), 99))
    
    for key in sorted_keys:
        item = grouped_findings[key]
        assets_str = ", ".join(item["assets"][:5])
        if len(item["assets"]) > 5:
            assets_str += f" y {len(item['assets']) - 5} más..."
            
        findings_data.append({
            "severity": item["severity"].upper(),
            "title": item["title"],
            "asset_ip": assets_str,
            "description": item["description"],
            "recommendation": item["recommendation"]
        })

    if type == "executive":
        findings_data = findings_data[:10]

    try:
        filename = report_gen.generate_pdf_report(
            client_name=client.name,
            stats=stats,
            findings=findings_data,
            lang=lang,
            type=type
        )
        
        # Update Snapshot
        snapshot.pdf_path = filename
        snapshot.pdf_url = f"/api/reports/download/{filename}"
        snapshot.status = "ready"
        db.commit()
        
    except Exception as e:
        snapshot.status = "error"
        db.commit()
        raise e

    return {
        "id": snapshot.id,
        "status": "ready",
        "download_url": snapshot.pdf_url,
        "lang": lang,
        "scan_context": scan_job.id,
        "assets_included": total_assets
    }

@router.get("/download/{filename}")
def download_report(filename: str):
    # Security check: filename should be just basename to prevent traversal
    safe_filename = os.path.basename(filename)
    filepath = os.path.join("/tmp/reports", safe_filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Report file not found")
    
    return FileResponse(filepath, media_type="application/pdf", filename=safe_filename)

@router.get("/clients/{client_id}/reports/{snapshot_id}/pdf")
def download_report_by_id(
    client_id: str,
    snapshot_id: str,
    db: Session = Depends(get_db)
):
    snapshot = db.query(ReportSnapshot).filter(
        ReportSnapshot.id == snapshot_id,
        ReportSnapshot.client_id == client_id
    ).first()
    
    if not snapshot or not snapshot.pdf_path:
        raise HTTPException(status_code=404, detail="Report Snapshot not found or PDF not ready")
        
    return download_report(snapshot.pdf_path)

