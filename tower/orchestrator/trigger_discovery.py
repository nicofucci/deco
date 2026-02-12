
import sys
import uuid
import os
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# DB Connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://jarvis_user:jarvis_password@deco-sec-db:5432/jarvis_core")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

CLIENT_ID = "45a5391a-a4fa-4364-84f0-1aa8c0dab72e" # Thinkpad

def trigger_discovery():
    db = SessionLocal()
    try:
        print(f"Triggering Discovery for Client: {CLIENT_ID}")
        
        # 1. Find Online Agent
        agent_query = text("SELECT id, primary_cidr, ip, hostname FROM agents WHERE client_id = :cid AND status = 'online' LIMIT 1")
        agent = db.execute(agent_query, {"cid": CLIENT_ID}).fetchone()
        
        if not agent:
            print("ERROR: No ONLINE agent found for this client.")
            return

        agent_id = agent.id
        target = agent.primary_cidr
        # Fix CIDR if needed
        if not target or target == "unknown":
             target = "192.168.100.0/24" # Default for Leoslo based on context
        
        print(f"Targeting Subnet: {target} via Agent: {agent_id} ({agent.hostname})")

        # 2. Create Job
        job_id = str(uuid.uuid4())
        insert_job = text("""
            INSERT INTO scan_jobs (id, client_id, agent_id, type, target, status, created_at, params)
            VALUES (:id, :cid, :aid, 'xray_network_scan', :tgt, 'pending', NOW(), :params)
        """)
        
        db.execute(insert_job, {
            "id": job_id,
            "cid": CLIENT_ID,
            "aid": agent_id,
            "tgt": target,
            "params": '{"mode": "full_discovery", "retroactive": true}'
        })
        db.commit()
        
        print(f"SUCCESS: Job {job_id} created. Status: PENDING.")
        
    except Exception as e:
        print(f"ERROR: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    trigger_discovery()
