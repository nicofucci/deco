import sys
import os
sys.path.append('/opt/deco/agent_runtime/jarvis_api')

from sqlalchemy import create_engine, inspect
from app.database import DATABASE_URL

def inspect_db():
    print(f"Connecting to {DATABASE_URL}")
    engine = create_engine(DATABASE_URL)
    inspector = inspect(engine)
    
    tables = inspector.get_table_names()
    print(f"Tables: {tables}")
    
    if 'cases' in tables:
        columns = [c['name'] for c in inspector.get_columns('cases')]
        print(f"Cases columns: {columns}")
        if 'asset_id' not in columns:
            print("MISSING asset_id in cases table")
        else:
            print("asset_id exists in cases table")
    else:
        print("cases table does NOT exist")

if __name__ == "__main__":
    inspect_db()
