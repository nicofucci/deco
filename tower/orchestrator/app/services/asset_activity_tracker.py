from sqlalchemy.orm import Session
from app.models.domain import NetworkAsset, NetworkAssetHistory
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger("DecoOrchestrator.AssetActivityTracker")
logger.setLevel(logging.INFO)

class AssetActivityTracker:
    def __init__(self, db: Session):
        self.db = db

    def process_scan_batch(self, client_id: int, agent_id: str, devices: List[Dict[str, Any]]):
        """
        Processes a batch of detected devices from X-RAY.
        Updates statuses, creates new assets, marks missing ones as 'gone' (if full scan).
        """
        logger.info(f"[ActivityTracker] Processing {len(devices)} devices for Client {client_id}")
        
        now = datetime.now(timezone.utc)
        current_ips = set()
        
        # 1. UPSERT / ACTIVE
        for device in devices:
            ip = device.get("ip")
            if not ip: continue
            current_ips.add(ip)
            
            asset = self.db.query(NetworkAsset).filter(
                NetworkAsset.client_id == client_id,
                NetworkAsset.ip == ip
            ).first()
            
            if asset:
                self._update_existing_asset(asset, device, agent_id, now)
            else:
                self._create_new_asset(client_id, agent_id, device, now)
        
        # 2. CHECK GONE (Implicit: if full network scan, missing items are gone?)
        # For V2, we assume X-RAY reports *all* visible neighbors in the subnet.
        # We mark assets as 'gone' if they are NOT in the current batch but belong to this client.
        # Note: Ideally we should filter by subnet, but for now we follow the simple V2 logic.
        
        all_client_assets = self.db.query(NetworkAsset).filter(
            NetworkAsset.client_id == client_id
        ).all()
        
        for asset in all_client_assets:
            if asset.ip not in current_ips:
                if asset.status != "gone":
                    # Only mark gone if it was previously seen reasonably recently?
                    # Or just immediately. V2 logic is immediate.
                    self._set_status(asset, "gone", "Not found in recent scan")
            else:
                 pass # Present, handled above

        self.db.commit()

    def _update_existing_asset(self, asset: NetworkAsset, device: Dict[str, Any], agent_id: str, now: datetime):
        # Update metadata
        asset.mac = device.get("mac") or asset.mac
        asset.mac_vendor = device.get("mac_vendor") or asset.mac_vendor
        asset.hostname = device.get("hostname") or asset.hostname
        asset.os_guess = device.get("os_guess") or asset.os_guess
        asset.device_type = device.get("device_type") or asset.device_type
        asset.open_ports = device.get("open_ports") or asset.open_ports
        asset.agent_id = agent_id # seen by this agent
        asset.last_seen = now
        asset.times_seen += 1
        
        old_status = asset.status
        
        # LOGIC: Transitions
        # Gone -> Stable/Active (Reappeared)
        if asset.status == "gone":
            self._set_status(asset, "stable", "Device reappeared")
        
        # New -> Stable (after X times or Y time)
        elif asset.status == "new":
            if asset.times_seen > 1 or (now - asset.first_seen > timedelta(hours=24)):
                 self._set_status(asset, "stable", "Promoted from new to stable")
        
        # Check Risk
        curr_status = asset.status # might have changed
        if self._is_at_risk(asset):
            if curr_status != "at_risk":
                 self._set_status(asset, "at_risk", "Critical ports or vulnerabilities detected")
        elif curr_status == "at_risk" and not self._is_at_risk(asset):
            # Resolve risk?
             self._set_status(asset, "stable", "Risk resolved")


    def _create_new_asset(self, client_id: int, agent_id: str, device: Dict[str, Any], now: datetime):
        asset = NetworkAsset(
            client_id=client_id,
            agent_id=agent_id,
            ip=device.get("ip"),
            mac=device.get("mac"),
            mac_vendor=device.get("mac_vendor"),
            hostname=device.get("hostname"),
            os_guess=device.get("os_guess"),
            device_type=device.get("device_type", "unknown"),
            open_ports=device.get("open_ports", []),
            first_seen=now,
            last_seen=now,
            times_seen=1,
            status="new"
        )
        self.db.add(asset)
        self.db.flush() # get ID
        self._log_history(asset, "created", "new", "First detection")

    def _set_status(self, asset: NetworkAsset, new_status: str, reason: str):
        if asset.status == new_status:
            return
        
        old_status = asset.status
        asset.status = new_status
        self._log_history(asset, old_status, new_status, reason)
    
    def _log_history(self, asset: NetworkAsset, old_status: str, new_status: str, reason: str):
        hist = NetworkAssetHistory(
            asset_id=asset.id,
            status=new_status,
            ip=asset.ip,
            mac=asset.mac,
            hostname=asset.hostname,
            changed_at=datetime.now(timezone.utc),
            reason=reason
        )
        self.db.add(hist)

    def _is_at_risk(self, asset: NetworkAsset) -> bool:
        # 1. Port based heuristics
        risky_ports = [3389, 445, 23] 
        if asset.open_ports:
            for p in asset.open_ports:
                if p in risky_ports:
                    return True
        
        # 2. Vuln based (if enrichment happened)
        # Assuming we check a relationship or count. 
        # For now, simplistic check if specialized_findings exist with 'critical' severity?
        # Or simple 'at_risk' status toggle.
        return False

    def mark_timed_out_assets(self, client_id: int, threshold_hours: int = 168): # 7 days default
        """
        Marks assets as 'gone' if not seen in threshold time.
        """
        cutoff = datetime.now(timezone.utc) - timedelta(hours=threshold_hours)
        assets = self.db.query(NetworkAsset).filter(
            NetworkAsset.client_id == client_id,
            NetworkAsset.status.in_(["new", "stable", "active", "at_risk"]),
            NetworkAsset.last_seen < cutoff
        ).all()
        
        count = 0
        for asset in assets:
            self._set_status(asset, "gone", f"Not seen for {threshold_hours}h")
            count += 1
        
        if count > 0:
            self.db.commit()
            logger.info(f"Marked {count} assets as gone for client {client_id}")
