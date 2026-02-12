import sys
import os
sys.path.append("/opt/deco/tower/orchestrator")

from app.db.session import SessionLocal
from app.models.domain import Agent, Client, ScanJob

db = SessionLocal()

from app.models.domain import Agent, Client, ScanJob, ScanResult, Asset, Finding

db = SessionLocal()

# List Jobs
jobs = db.query(ScanJob).all()
print(f"{'ID':<38} {'STATUS':<10} {'CLIENT_ID':<38} {'AGENT_ID':<38}")
print("-" * 130)
for j in jobs:
    print(f"{j.id:<38} {j.status:<10} {j.client_id:<38} {j.agent_id:<38}")

print("\n")

# List Results
results = db.query(ScanResult).all()
print(f"{'ID':<38} {'JOB_ID':<38} {'CREATED_AT'}")
print("-" * 100)
for r in results:
    print(f"{r.id:<38} {r.scan_job_id:<38} {r.created_at}")
    print(f"DATA: {str(r.raw_data)[:100]}...")

print("\n")

# List Assets
assets = db.query(Asset).all()
print(f"{'ID':<38} {'IP':<15} {'HOSTNAME':<20} {'CLIENT_ID'}")
print("-" * 100)
for a in assets:
    print(f"{a.id:<38} {a.ip:<15} {a.hostname:<20} {a.client_id}")

print("\n")

# List Findings
findings = db.query(Finding).all()
print(f"{'ID':<38} {'TITLE':<30} {'SEVERITY':<10} {'ASSET_ID'}")
print("-" * 100)
for f in findings:
    print(f"{f.id:<38} {f.title:<30} {f.severity:<10} {f.asset_id}")

db.close()
