from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.services.predictive_engine import PredictiveEngine
from app.models.domain import Client
import logging
import os

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DecoOrchestrator.PredictiveWorker")

# Hardcoded for reliability if needed, but trying settings first
DATABASE_URL = os.getenv("DATABASE_URL", settings.DATABASE_URL)

def run_analysis():
    logger.info("Starting Predictive Analysis Worker...")
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        clients = db.query(Client).filter(Client.status == "active").all()
        logger.info(f"Found {len(clients)} active clients.")
        
        predictor = PredictiveEngine(db)
        
        for client in clients:
            try:
                report = predictor.analyze_client(client.id)
                logger.info(f"Client {client.name} ({client.id}): Score {report.score}, Signals {len(report.signals)}")
            except Exception as e:
                logger.error(f"Error analyzing client {client.id}: {e}", exc_info=True)
                
    except Exception as e:
        logger.error(f"Worker failed: {e}", exc_info=True)
    finally:
        db.close()
        logger.info("Predictive Analysis Worker Finished.")

if __name__ == "__main__":
    run_analysis()
