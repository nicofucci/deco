import sys
import os

# Ensure the app directory is in the path
sys.path.append("/opt/deco/tower/orchestrator")

from app.db.session import engine
from app.db.base import Base
# Import all models to ensure they are registered with Base.metadata
from app.models import domain
from app.models import master_auth

def init_db():
    print("Initializing database...")
    print(f"Engine URL: {engine.url}")
    
    # Create all tables
    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")
    
    # List tables to verify
    from sqlalchemy import inspect
    ins = inspect(engine)
    tables = ins.get_table_names()
    print(f"Existing tables: {tables}")

if __name__ == "__main__":
    init_db()
