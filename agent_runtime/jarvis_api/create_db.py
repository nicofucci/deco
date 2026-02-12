import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def create_database():
    # Connect to default 'postgres' or 'jarvis_logs' db to create the new one
    # Try 'jarvis_logs' first as we know it exists from docker-compose
    try:
        conn = psycopg2.connect(
            user="jarvis",
            password="jarvis_db_password",
            host="localhost",
            port="5432",
            dbname="jarvis_logs"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        
        # Check if jarvis_chat exists
        cur.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'jarvis_chat'")
        exists = cur.fetchone()
        
        if not exists:
            print("Creating database jarvis_chat...")
            cur.execute("CREATE DATABASE jarvis_chat")
            print("Database jarvis_chat created successfully.")
        else:
            print("Database jarvis_chat already exists.")
            
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Error creating database: {e}")

if __name__ == "__main__":
    create_database()
