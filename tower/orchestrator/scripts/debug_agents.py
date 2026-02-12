from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.models.domain import Agent

db: Session = next(get_db())

print("--- AGENTS LIST ---")
agents = db.query(Agent).all()
for a in agents:
    print(f"ID: {a.id} | Host: {a.hostname} | Status: {a.status} | Client: {a.client_id}")
