from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.models.domain import Partner

db: Session = next(get_db())
partner = db.query(Partner).first()
if partner:
    print(f"Partner: {partner.name} | Key: {partner.partner_api_key}")
else:
    print("No partner found")
