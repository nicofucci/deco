import logging
import uuid
import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import Column, String, JSON, DateTime, ForeignKey, func
from app.db.base import Base

# We define the model here dynamically if needed, or mapped. 
# Better to have it in domain.py, but for now we can map it via Table reflection or just insert directly if lazy.
# Ideally, we should update domain.py first. Let's do that next step properly. 
# For now, I will assume the table exists and use direct SQL or defining a local model class to avoid import cycles 
# if domain.py update is pending. But the plan said update domain.py? No, plan said create table.
# Let's verify if I can update domain.py easily. Yes. I should update domain.py first.
# See next step. I will write the file content assuming the model exists in domain.py.

from app.models.domain import NetworkAsset, SpecializedFinding

logger = logging.getLogger(__name__)

class SpecializedScanner:
    def __init__(self, db: Session):
        self.db = db

    def process_result(self, job_type: str, asset: NetworkAsset, data: dict):
        """
        Generic entry point.
        """
        if job_type == "iot_deep_scan":
            return self.process_iot_result(asset, data)
        elif job_type == "smb_rdp_audit":
            return self.process_smb_result(asset, data)
        elif job_type == "critical_service_fingerprint":
            return self.process_fingerprint_result(asset, data)
        else:
            logger.warning(f"Unknown specialized job type: {job_type}")
            return None

    def process_iot_result(self, asset: NetworkAsset, data: dict):
        logger.info(f"[IoT] Processing deep scan for {asset.ip}")
        # Normalize/Filter data if needed
        # Example data: {"firmware": "1.0", "admin_panel": true, "upnp": {...}}
        
        severity = "info"
        if data.get("admin_panel", False) and data.get("default_creds", False):
            severity = "critical"
        elif data.get("firmware_vulnerable", False):
            severity = "high"

        return self._save_finding(asset.id, "iot_deep_scan", data, severity)

    def process_smb_result(self, asset: NetworkAsset, data: dict):
        logger.info(f"[SMB] Processing audit for {asset.ip}")
        # Example data: {"smb_v1": true, "signing": false}
        
        severity = "info"
        if data.get("smb_v1", False):
            severity = "critical"
        elif data.get("signing_required", False) is False:
             severity = "medium"

        return self._save_finding(asset.id, "smb_rdp_audit", data, severity)

    def process_fingerprint_result(self, asset: NetworkAsset, data: dict):
        logger.info(f"[Fingerprint] Processing for {asset.ip}")
        # Example data: {"ssh_banner": "OpenSSH 7.2...", "anonymous_ftp": true}
        
        severity = "info"
        if data.get("anonymous_ftp", False):
            severity = "high"
        if "telnet" in data:
            severity = "high"

        return self._save_finding(asset.id, "critical_service_fingerprint", data, severity)

    def _save_finding(self, asset_id: str, job_type: str, data: dict, severity: str):
        try:
            finding = SpecializedFinding(
                id=str(uuid.uuid4()),
                asset_id=asset_id,
                job_type=job_type,
                data=data,
                severity=severity,
                detected_at=datetime.now(timezone.utc)
            )
            self.db.add(finding)
            self.db.commit()
            logger.info(f"[+] Saved {job_type} finding for asset {asset_id}")
            return finding
        except Exception as e:
            logger.error(f"[-] Failed to save specialized finding: {e}")
            self.db.rollback()
            return None
