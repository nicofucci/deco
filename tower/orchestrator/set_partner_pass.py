import sys
import bcrypt
import os

sys.path.append('/app')
from app.db.session import SessionLocal
from app.models.domain import Partner

db = SessionLocal()
email = "partner@deco.security"
password = "partner_password_123"
pwd_bytes = password.encode('utf-8')
try:
    hashed = bcrypt.hashpw(pwd_bytes, bcrypt.gensalt()).decode('utf-8')
except Exception as e:
    print(f"Error hashing: {e}")
    sys.exit(1)

p = db.query(Partner).filter(Partner.email == email).first()
if not p:
    print(f"Creating partner {email}")
    p = Partner(email=email, name="Deco Partner", hashed_password=hashed, status="active")
    db.add(p)
else:
    print(f"Updating partner {email}")
    p.hashed_password = hashed
    p.status = "active"

db.commit()
print(f"SUCCESS: Partner {email} password set to {password}")
