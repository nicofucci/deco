import sys
import os
import logging
from datetime import datetime, timezone

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal, engine
from app.services.wti_engine import WTIEngine
from app.services.threat_correlation import ThreatCorrelationEngine
from app.models.domain import GlobalThreat, ClientThreatMatch, Client, NetworkAsset, NetworkVulnerability, Base

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("WTI_Verifier")

def verify_wti():
    # Ensure tables exist
    logger.info("Ensuring Database Schema...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        logger.info("--- Starting WTI Verification ---")
        
        # 1. Setup Data: Create Client & Asset if needed
        client = db.query(Client).filter(Client.name == "WTI_Test_Client").first()
        if not client:
            client = Client(name="WTI_Test_Client", contact_email="test@wti.local")
            db.add(client)
            db.commit()
            logger.info(f"Created Test Client: {client.id}")
            
        asset = db.query(NetworkAsset).filter(NetworkAsset.client_id == client.id, NetworkAsset.ip == "192.168.1.100").first()
        if not asset:
            asset = NetworkAsset(
                client_id=client.id, 
                ip="192.168.1.100", 
                hostname="win-server-prod", 
                os_guess="Windows Server 2019",
                device_type="server"
            )
            db.add(asset)
            db.commit()
            logger.info(f"Created Test Asset: {asset.id}")
            
        # 2. Inject Calculated Threat
        # Case A: CVE Match (Strong)
        # First, ensure asset has vulnerability
        vuln_cve = "CVE-2025-9999"
        vuln = db.query(NetworkVulnerability).filter(NetworkVulnerability.asset_id == asset.id, NetworkVulnerability.cve == vuln_cve).first()
        if not vuln:
            vuln = NetworkVulnerability(
                client_id=client.id,
                asset_id=asset.id,
                cve=vuln_cve,
                severity="critical"
            )
            db.add(vuln)
            db.commit()
            logger.info(f"Created Test Vulnerability: {vuln_cve}")

        threat_data = {
            "source": "manual_test",
            "cve": vuln_cve,
            "title": "Critical Zero-Day in Windows Server",
            "description": "RCE in Windows Server 2019 via SMB",
            "published_at": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "tags": ["zero-day", "exploit", "windows"],
            "exploit_status": "confirmed"
        }
        
        wti_engine = WTIEngine(db)
        if wti_engine._save_threat(threat_data):
            logger.info(f"Injected Threat: {vuln_cve}")
        else:
            logger.info(f"Threat {vuln_cve} already exists (skipping injection)")
            
        # Case B: Heuristic Match (Weak)
        threat_heuristic = {
            "source": "manual_test",
            "cve": "N/A",
            "title": "New PoC targeting Windows Server RDP",
            "description": "Potential RDP exploit",
            "published_at": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "tags": ["poc", "rdp"],
            "exploit_status": "poc"
        }
        if wti_engine._save_threat(threat_heuristic):
            logger.info("Injected Heuristic Threat")
            
        # 3. Run Correlation
        correlation = ThreatCorrelationEngine(db)
        matches = correlation.correlate_all()
        logger.info(f"Run Correlation. New Matches: {matches}")
        
        # 4. Verify Matches
        # Check Strong Match
        threat_strong = db.query(GlobalThreat).filter(GlobalThreat.cve == vuln_cve).first()
        match_strong = db.query(ClientThreatMatch).filter(
            ClientThreatMatch.client_id == client.id,
            ClientThreatMatch.threat_id == threat_strong.id,
            ClientThreatMatch.match_reason == "existing-vulnerability"
        ).first()
        
        if match_strong:
            logger.info("SUCCESS: Strong Match Verified (CVE Link)")
        else:
            logger.error("FAILURE: Strong Match NOT found")
            
        # Check Heuristic Match
        threat_weak = db.query(GlobalThreat).filter(GlobalThreat.title == threat_heuristic["title"]).first()
        # Heuristic match might rely on "os_guess" matching "windows" from title
        match_weak = db.query(ClientThreatMatch).filter(
            ClientThreatMatch.client_id == client.id,
            ClientThreatMatch.threat_id == threat_weak.id,
            ClientThreatMatch.match_reason.in_(["os-match", "device-match"])
        ).first()
         
        if match_weak:
             logger.info("SUCCESS: Heuristic Match Verified (OS Match)")
        else:
             logger.warning("WARNING: Heuristic Match NOT found (Check correlation logic)")
             
    except Exception as e:
        logger.error(f"Verification Failed: {e}", exc_info=True)
    finally:
        db.close()

if __name__ == "__main__":
    verify_wti()
