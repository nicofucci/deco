import sys
sys.path.append('/app')
from app.db.session import SessionLocal
from app.models.domain import Client, Partner

db = SessionLocal()
print("--- KEYS START ---")
clients = db.query(Client).all()
for c in clients:
    try:
        print(f"Client: {c.name}")
        print(f"  ID: {c.id}")
        print(f"  Panel Key: {c.client_panel_api_key}")
        print(f"  Agent Key: {c.agent_api_key}")
    except Exception as e:
        print(f"Error accessing client {c.name}: {e}")

partners = db.query(Partner).all()
for p in partners:
    print(f"Partner: {p.email} (Status: {p.status})")
print("--- KEYS END ---")
