import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Obtenemos la URL de la base de datos desde las variables de entorno
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL no está definido en el entorno. Revisa .env.deco_security y docker-compose.yml")

# future=True → API 2.0 de SQLAlchemy
engine = create_engine(
    DATABASE_URL,
    future=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
