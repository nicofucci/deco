import sys
sys.path.append('/app')
from app.db.session import SessionLocal
from app.models.domain import Client, Partner

db = SessionLocal()
print("--- KEYS START ---")

partners = db.query(Partner).all()
for p in partners:
    print(f"Partner: {p.email}")
    print(f"  ID: {p.id}")
    print(f"  Partner API Key: {p.partner_api_key}")

print("--- KEYS END ---")
