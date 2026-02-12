from app.db.session import SessionLocal
from app.models.domain import Partner
from app.core.security import get_password_hash

db = SessionLocal()
partner = db.query(Partner).filter(Partner.email == "nico@gmail.com").first()
if partner:
    print(f"Found partner: {partner.name}")
    partner.hashed_password = get_password_hash("nico123")
    db.commit()
    print("Password reset to 'nico123'")
else:
    print("Partner not found")
db.close()
