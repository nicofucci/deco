import asyncio
import logging
import redis.asyncio as aioredis
from app.database import SessionLocal
from app.services.alerts_service import create_alert_from_event

logger = logging.getLogger(__name__)

async def start_redis_monitor_watcher():
    """
    Monitor Redis.
    Runs every 60 seconds.
    """
    logger.info("Starting Redis Monitor Watcher...")
    while True:
        try:
            await check_redis()
        except Exception as e:
            logger.error(f"Error in Redis Monitor Watcher: {e}")
        
        await asyncio.sleep(60)

async def check_redis():
    db = SessionLocal()
    try:
        try:
            redis = aioredis.from_url("redis://redis:6379", encoding="utf-8", decode_responses=True)
            if not await redis.ping():
                raise Exception("Ping failed")
            await redis.close()
        except Exception as e:
            create_alert_from_event(
                db,
                event_type="SYSTEM",
                severity="critical",
                source="redis_monitor",
                title="Redis Down",
                description=f"Could not connect to Redis: {str(e)}",
                metadata={"error": str(e)}
            )
    finally:
        db.close()
