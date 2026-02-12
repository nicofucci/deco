import sys
import os
from sqlalchemy import text

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine

def reset_alerts_table():
    with engine.connect() as conn:
        print("Dropping system_alerts table...")
        conn.execute(text("DROP TABLE IF EXISTS system_alerts CASCADE"))
        conn.commit()
        print("Table dropped.")

if __name__ == "__main__":
    reset_alerts_table()
