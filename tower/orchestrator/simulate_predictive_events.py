import logging
import uuid
import sys
import os
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append("/app")

# from app.core.config import settings
from app.models.domain import Client, NetworkAsset, NetworkVulnerability, PredictiveSignal
from app.services.predictive_engine import PredictiveEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DecoPredictiveSim")

# Hardcode DB URL if needed, else use settings
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://deco:deco123@postgres:5432/decocore")

def run_simulation():
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        # 1. Create Test Client
        client_id = f"test-pred-{uuid.uuid4().hex[:6]}"
        logger.info(f"Creating test client: {client_id}")
        
        client = Client(id=client_id, name="Predictive Test Corp", status="active")
        db.add(client)
        db.commit()
        
        # 2. Simulate "New Device Surge" (Add 5 new assets)
        logger.info("Simulating NEW DEVICE SURGE (5 new assets)...")
        for i in range(5):
            asset = NetworkAsset(
                id=str(uuid.uuid4()),
                client_id=client_id,
                ip=f"192.168.99.{100+i}",
                status="new",
                device_type="iot",
                first_seen=datetime.now()
            )
            db.add(asset)
            
        # 3. Simulate "Critical Vuln Spike" (Add 3 critical vulns)
        logger.info("Simulating CRITICAL VULN SPIKE (3 critical CVEs)...")
        asset_id = str(uuid.uuid4())
        vuln_asset = NetworkAsset(
             id=asset_id,
             client_id=client_id,
             ip="192.168.99.200",
             status="stable",
             device_type="server"
        )
        db.add(vuln_asset)
        
        for i in range(3):
            vuln = NetworkVulnerability(
                id=str(uuid.uuid4()),
                client_id=client_id,
                asset_id=asset_id,
                cve=f"CVE-2025-900{i}",
                severity="critical",
                first_detected=datetime.now()
            )
            db.add(vuln)
            
        db.commit()
        
        # 4. Run Analysis
        logger.info("Running Predictive Engine Analysis...")
        engine = PredictiveEngine(db)
        report = engine.analyze_client(client_id)
        
        logger.info(f"Analysis Result -> Score: {report.score}")
        for s in report.signals:
            logger.info(f"Signal: [{s['severity']}] {s['type']} - {s['description']} ({s['score_delta']})")
            
        # 5. Assertions
        assert report.score < 100, "Score should have decreased"
        assert any(s['type'] == 'new_device_surge' for s in report.signals), "Should detect new device surge"
        assert any(s['type'] == 'critical_vuln_spike' for s in report.signals), "Should detect vuln spike"
        
        # Verify persistence
        db_signals = db.query(PredictiveSignal).filter(PredictiveSignal.client_id==client_id).all()
        assert len(db_signals) >= 2, "Signals should be persisted in DB"
        
        updated_client = db.query(Client).filter(Client.id==client_id).first()
        assert updated_client.predictive_risk_score == report.score, "Client risk score should be updated in DB"
        
        logger.info("SUCCESS: Predictive System Verified (Backend).")
        
        # Cleanup
        logger.info("Cleaning up...")
        db.query(PredictiveSignal).filter(PredictiveSignal.client_id==client_id).delete()
        db.query(NetworkVulnerability).filter(NetworkVulnerability.client_id==client_id).delete()
        db.query(NetworkAsset).filter(NetworkAsset.client_id==client_id).delete()
        db.query(Client).filter(Client.id==client_id).delete()
        db.commit()
        
    except Exception as e:
        logger.error(f"Simulation failed: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    run_simulation()
