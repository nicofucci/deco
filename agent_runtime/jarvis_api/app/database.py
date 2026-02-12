import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.chat import Base
from app.models.ai_benchmarks import AIAgentVersion, AIAgentBenchmark
from app.models.alerts import SystemAlert
from app.risk.risk_model import RiskScore
from app.models.actions import ProposedAction
from app.models.jarvis_console import JarvisConsoleMessage

# Use environment variable or default to local postgres
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://jarvis:jarvis_db_password@localhost:5432/jarvis_chat")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    # Create tables if they don't exist (simple migration for now)
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
