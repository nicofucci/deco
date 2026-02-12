#!/usr/bin/env python
"""
CLE Manual Trigger Script
Runs a single learning cycle manually
"""

import sys
import os
import asyncio
import logging

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.cle.scheduler import LearningCycleOrchestrator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


async def main():
    """Run a manual learning cycle"""
    logger.info("🧠 Starting JARVIS CLE Manual Learning Cycle...")
    
    try:
        orchestrator = LearningCycleOrchestrator()
        
        # Example sources (customize as needed)
        web_urls = [
            "https://owasp.org/www-project-top-ten/",
            "https://www.kali.org/docs/general-use/kali-tools/",
        ]
        
        github_topics = ["penetration-testing", "security-tools"]
        
        report_path = await orchestrator.run_learning_cycle(
            web_urls=web_urls,
            github_topics=github_topics,
            youtube_urls=None
        )
        
        logger.info(f"✅ Learning cycle completed!")
        logger.info(f"📄 Report: {report_path}")
        print(f"\n✅ SUCCESS! Report generated at:\n   {report_path}\n")
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ Learning cycle failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
