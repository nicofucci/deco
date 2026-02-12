import asyncio
from sqlalchemy import delete
from app.database import SessionLocal
from app.models.alerts import SystemAlert

async def cleanup_alerts():
    db = SessionLocal()
    try:
        print("Cleaning up old 'Agent Inactivity' alerts...")
        # Delete alerts with title "Agent Inactivity" created before today (or just all of them to start fresh)
        # User asked to "Eliminate automatic creation... and remove old or senseless alerts"
        # Let's delete all "Agent Inactivity" alerts to be safe and clean.
        
        stmt = delete(SystemAlert).where(SystemAlert.title.like("%Agent Inactivity%"))
        result = db.execute(stmt)
        db.commit()
        print(f"Deleted {result.rowcount} old inactivity alerts.")
        
    except Exception as e:
        print(f"Error cleaning alerts: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(cleanup_alerts())
