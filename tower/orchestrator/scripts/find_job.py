from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.models.domain import ScanJob

db: Session = next(get_db())
job_id = "78ce88df-bae8-4a6e-863a-c51260f0a926"
job = db.query(ScanJob).filter(ScanJob.id == job_id).first()

if job:
    print(f"FOUND: Job ID: {job.id} | Status: {job.status} | Agent: {job.agent_id} | Created: {job.created_at}")
else:
    print("Job NOT FOUND")
