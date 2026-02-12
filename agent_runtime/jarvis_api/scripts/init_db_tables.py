import sys
import os

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import init_db

if __name__ == "__main__":
    print("Initializing database tables...")
    init_db()
    print("Tables initialized.")
