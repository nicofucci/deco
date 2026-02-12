from sqlalchemy.orm import declarative_base

# Base común para todos los modelos SQLAlchemy
# Base común para todos los modelos SQLAlchemy
Base = declarative_base()

# Import models for side-effects (registration)
from app.models.master_auth import MasterAdmin, MasterWebAuthnCredential
