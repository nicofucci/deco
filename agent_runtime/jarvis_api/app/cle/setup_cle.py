#!/usr/bin/env python
"""
CLE Setup Script
Initializes Qdrant collections for Continuous Learning Engine
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.cle.qdrant_manager import CLEQdrantManager
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def main():
    """Initialize CLE collections"""
    logger.info("🚀 Starting CLE Setup...")
    
    try:
        # Connect to Qdrant
        logger.info("Connecting to Qdrant...")
        manager = CLEQdrantManager(host="localhost", port=6333)
        
        # Create collections
        logger.info("Creating CLE collections...")
        manager.setup_collections()
        
        # Verify
        counts = manager.get_total_knowledge_count()
        logger.info("✅ CLE Setup Complete!")
        logger.info(f"Collections status: {counts}")
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ CLE Setup failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
