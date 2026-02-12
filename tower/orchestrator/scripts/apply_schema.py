
import os
import sys

# Add app to path
sys.path.append(os.getcwd())

from app.db.base import Base
from app.db.session import engine
from app.models import domain # Import models to ensure they are registered

def apply_schema():
    print("Applying schema updates...")
    Base.metadata.create_all(bind=engine)
    print("Schema applied successfully.")

if __name__ == "__main__":
    apply_schema()
