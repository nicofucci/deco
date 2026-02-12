import logging
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models.domain import NetworkAsset, NetworkVulnerability
from app.services.vuln_providers import NvdVulnProvider

logger = logging.getLogger(__name__)

class CPEClassifier:
    """
    Classifies Assets into CPEs based on Ports, OS, and Banners.
    """
    def guess_cpe(self, asset: NetworkAsset) -> List[str]:
        cpes = set()
        
        # 1. OS Heuristics
        os_guess = str(asset.os_guess).lower() if asset.os_guess else ""
        if "windows" in os_guess:
            # Fixed for NVD 2.0 (Generic Windows 10 base)
            cpes.add("cpe:2.3:o:microsoft:windows_10:-:*:*:*:*:*:*:*")
        elif "linux" in os_guess or "ubuntu" in os_guess:
            # Linux Kernel Generic
            cpes.add("cpe:2.3:o:linux:linux_kernel:-:*:*:*:*:*:*:*")
            
        # 2. Port Heuristics
        ports = asset.open_ports or []
        
        # Windows services - Generic OS CPE handles most, but specific apps?
        # NVD 2.0 requires valid CPE 2.3 strings basically.
        # "cpe:/o:microsoft:windows" is CPE 2.2, NVD prefers 2.3.
        # Using broad 2.3 strings.
            
        # Web Servers (Blind guess)
        if 80 in ports or 443 in ports:
             # cpes.add("cpe:2.3:a:apache:http_server:*:*:*:*:*:*:*:*") # Risk of false pos if nginx
             pass
            
        return list(cpes)

class CVEEnricher:
    """
    Looks up CVEs via Cache or NVD.
    """
    def __init__(self, db: Session):
        self.db = db
        self.provider = NvdVulnProvider()
        self.cache_ttl = timedelta(days=7)

    def search_cves(self, cpes: List[str]) -> List[Dict[str, Any]]:
        findings = []
        for cpe in cpes:
            findings.extend(self._get_cves_for_cpe(cpe))
        return findings
        
    def _get_cves_for_cpe(self, cpe: str) -> List[Dict[str, Any]]:
        # 1. Check Cache
        try:
            result = self.db.execute(
                text("SELECT cves, last_updated FROM cve_cache WHERE cpe = :cpe"),
                {"cpe": cpe}
            ).fetchone()
            
            if result:
                cves_json = result[0]
                last_updated = result[1]
                # Allow generic datetime comparisons (aware vs naive can be tricky, assuming naive or UTC)
                if last_updated and (datetime.utcnow() - last_updated.replace(tzinfo=None)) < self.cache_ttl:
                    logger.info(f"[Enricher] Cache HIT for {cpe}")
                    # Hydrate CPE back into items
                    data = cves_json if isinstance(cves_json, list) else json.loads(cves_json)
                    for item in data:
                        item["cpe"] = cpe
                    return data
            
            logger.info(f"[Enricher] Cache MISS/EXPIRED for {cpe}")
        except Exception as e:
            logger.error(f"[Enricher] Cache read error: {e}")

        # 2. Fetch from NVD
        cves = self.provider.fetch_cves_for_cpe(cpe)
        
        # 3. Update Cache
        try:
            # Postgres UPSERT
            stmt = text("""
                INSERT INTO cve_cache (cpe, cves, last_updated) 
                VALUES (:cpe, :cves, :now)
                ON CONFLICT (cpe) DO UPDATE 
                SET cves = EXCLUDED.cves, last_updated = EXCLUDED.last_updated
            """)
            self.db.execute(stmt, {
                "cpe": cpe, 
                "cves": json.dumps(cves), 
                "now": datetime.utcnow()
            })
            self.db.commit()
        except Exception as e:
            logger.error(f"[Enricher] Cache write error: {e}")
            self.db.rollback()

        # Add CPE field to results
        for item in cves:
            item["cpe"] = cpe
            
        return cves

class EnrichmentService:
    def __init__(self, db: Session):
        self.db = db
        self.classifier = CPEClassifier()
        self.enricher = CVEEnricher(db)

    def process_asset(self, asset: NetworkAsset):
        """
        Main entry point: Classification -> Enrichment -> Persistence.
        """
        try:
            # 1. Classify
            cpes = self.classifier.guess_cpe(asset)
            if not cpes:
                return 0
                
            # 2. Key external sources
            cves = self.enricher.search_cves(cpes)
            
            # 3. Persist
            count = 0
            for vuln_data in cves:
                # Check duplication
                exists = self.db.query(NetworkVulnerability).filter(
                    NetworkVulnerability.asset_id == asset.id,
                    NetworkVulnerability.cve == vuln_data["cve"]
                ).first()
                
                if exists:
                    exists.last_detected = datetime.utcnow()
                    continue
                    
                # Create New
                new_vuln = NetworkVulnerability(
                    client_id=asset.client_id,
                    asset_id=asset.id,
                    agent_id=asset.agent_id,
                    cpe=vuln_data["cpe"],
                    cve=vuln_data["cve"],
                    cvss_score=vuln_data["score"],
                    severity=vuln_data["severity"].lower(),
                    description_short=vuln_data["desc"][:250] if vuln_data["desc"] else "No description",
                    exploit_available=vuln_data["exploit"],
                    exploit_sources=["nvd"]
                )
                self.db.add(new_vuln)
                count += 1
                
            self.db.commit()
            if count > 0:
                logger.info(f"[+] Enriched Asset {asset.ip}: Found {count} new vulnerabilities.")
            return count
            
        except Exception as e:
            logger.error(f"[-] Error enriching asset {asset.id}: {e}", exc_info=True)
            self.db.rollback()
            return 0
