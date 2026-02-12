import sys
sys.path.append('/app')
from app.db.session import SessionLocal
from app.models.domain import Client, Partner

db = SessionLocal()
client_id = "2538b150-8d2a-4b45-ac31-f39f270d7113" # ID of AutofixClient_1fff722c from previous dump
partner_email = "partner@deco.security"

partner = db.query(Partner).filter(Partner.email == partner_email).first()
client = db.query(Client).filter(Client.id == client_id).first()

if partner and client:
    print(f"Linking Client {client.name} ({client.id}) to Partner {partner.email} ({partner.id})")
    client.partner_id = partner.id
    db.commit()
    print("SUCCESS")
else:
    print("Partner or Client not found")
