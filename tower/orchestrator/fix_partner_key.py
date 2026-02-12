import sys
sys.path.append('/app')
from app.db.session import SessionLocal
from app.models.domain import Partner

db = SessionLocal()
email = "partner@deco.security"
key = "deco-partner-key-123"

p = db.query(Partner).filter(Partner.email == email).first()
if p:
    print(f"Updating partner {email} with key {key}")
    p.partner_api_key = key
    db.commit()
    print("SUCCESS")
else:
    print("Partner not found")
