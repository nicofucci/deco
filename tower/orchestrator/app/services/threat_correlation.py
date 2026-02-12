
import logging
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.domain import GlobalThreat, ClientThreatMatch, NetworkAsset, NetworkVulnerability, Client

logger = logging.getLogger(__name__)

class ThreatCorrelationEngine:
    """
    Correlates Global Threat Intelligence with specific Client Assets.
    Generates ClientThreatMatch records.
    """

    def __init__(self, db: Session):
        self.db = db

    def correlate_all(self):
        """
        Runs correlation for all unprocessed global threats.
        """
        unprocessed_threats = self.db.query(GlobalThreat).filter(GlobalThreat.processed == False).all()
        logger.info(f"Correlating {len(unprocessed_threats)} new global threats...")
        
        matches_count = 0
        for threat in unprocessed_threats:
            matches = self._find_matches_for_threat(threat)
            for match in matches:
                self.db.add(match)
                matches_count += 1
            
            threat.processed = True
            
        self.db.commit()
        logger.info(f"Correlation complete. Generated {matches_count} client alerts.")
        return matches_count

    def _find_matches_for_threat(self, threat: GlobalThreat):
        matches = []
        
        # Strategy 1: CVE Match (Strongest)
        # Check if any client asset has this CVE already detected by scanner
        if threat.cve and threat.cve != "N/A":
            vuln_matches = self.db.query(NetworkVulnerability).filter(NetworkVulnerability.cve == threat.cve).all()
            for vuln in vuln_matches:
                # Avoid duplicates
                if not self._match_exists(vuln.client_id, threat.id, vuln.asset_id):
                    matches.append(ClientThreatMatch(
                        client_id=vuln.client_id,
                        threat_id=threat.id,
                        asset_id=vuln.asset_id,
                        match_reason="existing-vulnerability",
                        risk_level="critical" if threat.exploit_status == "confirmed" else "high",
                        status="active"
                    ))

        # Strategy 2: Keyword/Tag Heuristic Match (Broad)
        # e.g. Threat Title mentions "Windows Server" and tags include "RDP"
        # This is expensive so we do it sparingly or via simple text search on assets
        
        keywords = threat.title.lower().split()
        target_os = None
        target_device = None
        
        if "windows" in keywords: target_os = "windows"
        if "linux" in keywords: target_os = "linux"
        if "android" in keywords: target_os = "android"
        
        if "router" in keywords or "tp-link" in keywords: target_device = "router"
        if "printer" in keywords: target_device = "printer"

        if target_os or target_device:
            # Query candidate assets
            query = self.db.query(NetworkAsset).join(Client).filter(Client.status == "active")
            
            if target_os:
                query = query.filter(or_(NetworkAsset.os_guess.ilike(f"%{target_os}%"), NetworkAsset.os_guess.ilike(f"%{target_os}%")))
            if target_device:
                 query = query.filter(NetworkAsset.device_type == target_device)

            # Limit impact blast radius for heuristics to avoid spam
            assets = query.limit(100).all() 
            
            for asset in assets:
                # Only match if we haven't matched by CVE already
                # (Simple check: dedupe list before return?)
                if not self._match_exists(asset.client_id, threat.id, asset.id):
                    matches.append(ClientThreatMatch(
                        client_id=asset.client_id,
                        threat_id=threat.id,
                        asset_id=asset.id,
                        match_reason="os-match" if target_os else "device-match",
                        risk_level="medium", # Lower confidence
                        status="active"
                    ))

        return matches

    def _match_exists(self, client_id, threat_id, asset_id):
        return self.db.query(ClientThreatMatch).filter(
            ClientThreatMatch.client_id == client_id,
            ClientThreatMatch.threat_id == threat_id,
            ClientThreatMatch.asset_id == asset_id
        ).count() > 0
