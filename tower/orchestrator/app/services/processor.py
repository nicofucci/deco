from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.domain import ScanResult, Asset, Finding, ScanJob, Agent, NetworkAsset
from app.services.parser import FindingsParser
from datetime import datetime, timezone
from typing import Any, Dict, List
import logging

logger = logging.getLogger("DecoOrchestrator.Processor")
logger.setLevel(logging.INFO)

def process_scan_result(result_id: str):
    """
    Background task to process a scan result.
    """
    db: Session = SessionLocal()
    try:
        logger.info(f"[*] Processing ScanResult: {result_id}")
        result = db.query(ScanResult).filter(ScanResult.id == result_id).first()
        if not result:
            print(f"[-] Result {result_id} not found.")
            return

        # Fetch related context
        job = db.query(ScanJob).filter(ScanJob.id == result.scan_job_id).first()
        agent = db.query(Agent).filter(Agent.id == job.agent_id).first()
        
        if not job or not agent:
            logger.info("[-] Missing Job or Agent context.")
            return

        logger.info(f"[DEBUG] Processing Job Type: '{job.type}' for Result: {result_id}")

        # X-RAY NETWORK SCAN LOGIC
        if job.type == "xray_network_scan":
            _process_xray_scan(db, job, agent, result.raw_data)
            return

        # SPECIALIZED DEEP SCANS (Task 1.3)
        specialized_types = ["iot_deep_scan", "smb_rdp_audit", "critical_service_fingerprint"]
        if job.type in specialized_types:
            _process_specialized_scan(db, job, result.raw_data)
            return

        parser = FindingsParser()
        raw_data = result.raw_data or {}
        
        # ... validation fallback ...
        hosts_payload = raw_data.get("hosts") if isinstance(raw_data, dict) else None
        host_entries: List[Dict[str, Any]] = []
        if isinstance(hosts_payload, list):
            for h in hosts_payload:
                if isinstance(h, dict):
                    host_entries.append(h)
                elif isinstance(h, str):
                    host_entries.append({"ip": h})

        if not host_entries:
            target_ips = _collect_targets(raw_data, job.target)
            host_entries = [{"ip": ip} for ip in target_ips]

        total_findings = 0
        for host in host_entries:
            ip = _normalize_target(host.get("ip"))
            if not ip:
                continue

            asset = (
                db.query(Asset)
                .filter(
                    Asset.client_id == job.client_id,
                    Asset.ip == ip
                )
                .first()
            )

            if not asset:
                asset = Asset(
                    client_id=job.client_id,
                    ip=ip,
                    hostname=host.get("hostname") or raw_data.get("hostname") or ip,
                    created_at=datetime.now(timezone.utc)
                )
                db.add(asset)
                db.commit()
                db.refresh(asset)

            ports = host.get("open_ports") or host.get("ports") or []
            host_raw = dict(raw_data)
            host_raw.update({"ports": ports, "open_ports": ports, "target": ip})

            detected = parser.parse(host_raw)
            if detected:
                for f_data in detected:
                    finding = Finding(
                        client_id=job.client_id,
                        asset_id=asset.id,
                        severity=f_data.severity,
                        title=f_data.title,
                        description=f_data.description,
                        recommendation=f_data.recommendation,
                        detected_at=datetime.now(timezone.utc)
                    )
                    db.add(finding)
                    _update_global_stats(f_data.title, f_data.severity)
                total_findings += len(detected)

        db.commit()
        print(f"[+] Procesado resultado {result_id}: assets={len(host_entries)}, findings={total_findings}")

    except Exception as e:
        logger.error(f"[-] Error processing result {result_id}: {e}", exc_info=True)
    finally:
        db.close()

def _process_xray_scan(db: Session, job: ScanJob, agent: Agent, raw_data: Dict[str, Any]):
    """
    Procesa resultados de X-RAY Network Scan y actualiza NetworkAsset.
    V2: Usa AssetActivityTracker.
    """
    from app.services.asset_activity_tracker import AssetActivityTracker
    
    devices = raw_data.get("devices", [])
    logger.info(f"[DEBUG] _process_xray_scan invoked. Devices count: {len(devices)}")
    
    # Check for error message
    if raw_data.get("message") and "not implemented" in raw_data.get("message").lower():
        logger.error(f"[-] X-RAY job {job.id} failed: Agent does not support X-RAY (Update Required).")
        return
        
    if not devices:
        logger.info(f"[-] X-RAY job {job.id} returned no devices.")
        return

    tracker = AssetActivityTracker(db)
    tracker.process_scan_batch(job.client_id, agent.id, devices)
    
    # 2. TRIGGER VULNERABILITY ENRICHMENT (Task 1.2)
    try:
        from app.services.enrichment import EnrichmentService
        enricher = EnrichmentService(db)
        
        # Re-query active assets to ensure we have latest state
        active_assets = db.query(NetworkAsset).filter(
            NetworkAsset.client_id == job.client_id,
            NetworkAsset.status.in_(["new", "stable", "at_risk"])
        ).all()
        
        total_vulns = 0
        for asset in active_assets:
            total_vulns += enricher.process_asset(asset)
            
        logger.info(f"[+] Enrichment Complete: Added {total_vulns} vulnerabilities across {len(active_assets)} assets.")
        
    except Exception as e:
        logger.error(f"[-] Enrichment Failed: {e}", exc_info=True)  


def _collect_targets(raw_data: Dict[str, Any], fallback_target: str) -> List[str]:
    """
    Normaliza los posibles IPs/hostnames reportados por el agente.
    """
    targets: List[str] = []
    if isinstance(raw_data, dict):
        if isinstance(raw_data.get("hosts"), list):
            targets.extend(
                [_normalize_target(h) for h in raw_data["hosts"] if isinstance(h, str)]
            )
        if raw_data.get("target"):
            targets.append(_normalize_target(raw_data["target"]))

    if not targets and fallback_target:
        targets.append(_normalize_target(fallback_target))

    # Deduplicamos preservando orden
    seen = set()
    unique_targets = []
    for t in targets:
        if t not in seen:
            unique_targets.append(t)
            seen.add(t)
    return unique_targets


def _normalize_target(target: Any) -> str:
    """
    Devuelve un string de IP/host limpio (sin CIDR).
    """
    target_ip = str(target)
    if "/" in target_ip:
        target_ip = target_ip.split("/")[0]
    return target_ip

def _update_global_stats(threat_title: str, severity: str):
    """
    Updates global threat counters in Redis for real-time dashboard.
    """
    try:
        import redis
        import os
        redis_url = os.getenv('REDIS_URL', 'redis://deco-sec-redis:6379')
        r = redis.from_url(redis_url)
        
        # Increment global counter
        r.incr("global:threats:total")
        
        # Increment by severity
        r.incr(f"global:threats:severity:{severity.lower()}")
        
        # Increment by threat title (Top Threats)
        r.zincrby("global:threats:top", 1, threat_title)
        
    except Exception as e:
        print(f"Error updating global stats: {e}")

def _process_specialized_scan(db: Session, job: ScanJob, raw_data: Dict[str, Any]):
    """
    Task 1.3: Handles IoT/SMB/Fingerprint scan results.
    """
    from app.services.specialized_scanner import SpecializedScanner
    
    logger.info(f"[*] specialized scan processing for Job {job.id} ({job.type})")
    
    # We expect raw_data to contain "target_ip" or we use job.target
    target_ip = raw_data.get("target_ip") or job.target
    if not target_ip:
        logger.error(f"[-] Specialized job {job.id} has no target IP.")
        return

    # Find the NetworkAsset
    asset = db.query(NetworkAsset).filter(
        NetworkAsset.client_id == job.client_id,
        NetworkAsset.ip == str(target_ip)
    ).first()
    
    if not asset:
        logger.error(f"[-] Asset {target_ip} not found for specialized scan.")
        # Optional: Create it? No, Deep Scan implies X-RAY found it first.
        return
        
    scanner = SpecializedScanner(db)
    scanner.process_result(job.type, asset, raw_data)
    logger.info(f"[+] Specialized scan {job.type} processed for {asset.ip}")
