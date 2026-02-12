from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.models.domain import Agent, ScanJob, Client
from datetime import datetime
import json

db: Session = next(get_db())

print("--- AGENTS ---")
agents = db.query(Agent).all()
for a in agents:
    print(f"Agent ID: {a.id} | Hostname: {a.hostname} | Status: {a.status} | Last Seen: {a.last_seen_at}")

print("\n--- RECENT JOBS (Last 10) ---")
jobs = db.query(ScanJob).order_by(ScanJob.created_at.desc()).limit(10).all()
for j in jobs:
    print(f"Job ID: {j.id} | Type: {j.type} | Status: {j.status} | Agent ID: {j.agent_id}")
