
import sys
import os
import logging
import json

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.models.domain import Client, ScanJob, ScanResult, NetworkAsset
from sqlalchemy import desc

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("XRAY_Diag")

def diagnose():
    db = SessionLocal()
    try:
        # 1. Find Client
        logger.info("--- 1. Locating Client ---")
        client = db.query(Client).filter(Client.name.ilike("%iMac%")).first()
        if not client:
            logger.info("Client 'iMac' not found. Fetching last active client with jobs...")
            # optimize: join with scanjobs
            last_job = db.query(ScanJob).filter(ScanJob.type == "xray_network_scan").order_by(desc(ScanJob.created_at)).first()
            if last_job:
                client = db.query(Client).get(last_job.client_id)
        
        if not client:
            logger.error("No suitable client found for diagnosis.")
            return

        logger.info(f"Target Client: {client.name} ({client.id})")

        # 2. Find Last X-RAY Job
        logger.info("--- 2. Checking Last X-RAY Job ---")
        job = db.query(ScanJob).filter(
            ScanJob.client_id == client.id,
            ScanJob.type == "xray_network_scan",
            ScanJob.status == "done"
        ).order_by(desc(ScanJob.created_at)).first()

        if not job:
            logger.error("No completed xray_network_scan found for this client.")
        else:
            logger.info(f"Job Found: {job.id} | Finished: {job.finished_at}")
            
            # 3. Check Result
            result = db.query(ScanResult).filter(ScanResult.scan_job_id == job.id).first()
            if not result or not result.raw_data:
                logger.error("Job accepted as DONE but has NO result data in DB!")
            else:
                data = result.raw_data
                # Assuming raw_data is a list of hosts or dict
                if isinstance(data, str):
                    try:
                        data = json.loads(data)
                    except:
                        pass
                
                logger.info(f"Raw Data Type: {type(data)}")
                logger.info(f"Raw Data Sample (first 200 chars): {str(data)[:200]}")
                
                if isinstance(data, list):
                    logger.info(f"Host Count in Raw Data: {len(data)}")
                elif isinstance(data, dict):
                    # Maybe nmap xml converted?
                    logger.info(f"Keys in Raw Data: {data.keys()}")

        # 4. Check Network Assets
        logger.info("--- 3. Checking Network Assets Table ---")
        assets = db.query(NetworkAsset).filter(NetworkAsset.client_id == client.id).all()
        logger.info(f"Total Network Assets in DB: {len(assets)}")
        
        for i, asset in enumerate(assets[:5]):
            logger.info(f"Asset {i+1}: IP={asset.ip}, Hostname={asset.hostname}, Status={asset.status}")

    except Exception as e:
        logger.error(f"Diagnosis Failed: {e}", exc_info=True)
    finally:
        db.close()

if __name__ == "__main__":
    diagnose()
