
import logging
import time
from app.db.session import SessionLocal
from app.services.wti_engine import WTIEngine
from app.services.threat_correlation import ThreatCorrelationEngine

logger = logging.getLogger(__name__)

def run_wti_cycle():
    """
    Worker Entry Point:
    1. Fetches Intelligence
    2. Runs Correlation
    """
    logger.info("WTI Worker cycle starting...")
    db = SessionLocal()
    try:
        engine = WTIEngine(db)
        correlation = ThreatCorrelationEngine(db)
        
        # 1. Fetch
        new_items = engine.fetch_threat_intel()
        
        # 2. Correlate
        matches = correlation.correlate_all()
        
        logger.info(f"WTI Cycle Done. Items: {new_items}, Matches: {matches}")
    except Exception as e:
        logger.error(f"Error in WTI worker: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    # If run standalone
    run_wti_cycle()
