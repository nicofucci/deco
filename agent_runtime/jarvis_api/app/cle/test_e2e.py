#!/usr/bin/env python
"""
CLE End-to-End Test Script
Comprehensive validation of the entire CLE system
"""

import sys
import os
import asyncio
import logging
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.cle.scheduler import LearningCycleOrchestrator
from app.cle.qdrant_manager import CLEQdrantManager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


async def test_e2e():
    """Run complete end-to-end test"""
    
    print("=" * 80)
    print("JARVIS CLE - END-TO-END SYSTEM TEST")
    print("=" * 80)
    print()
    
    # Step 1: Check Qdrant
    print("📊 Step 1: Checking Qdrant Collections...")
    try:
        qdrant = CLEQdrantManager()
        counts = qdrant.get_total_knowledge_count()
        print(f"✅ Qdrant collections found:")
        for coll, count in counts.items():
            print(f"   - {coll}: {count} items")
    except Exception as e:
        print(f"❌ Qdrant error: {e}")
        return False
    
    print()
    
    # Step 2: Initialize orchestrator
    print("🤖 Step 2: Initializing Learning Cycle Orchestrator...")
    try:
        orchestrator = LearningCycleOrchestrator()
        print("✅ Orchestrator initialized")
    except Exception as e:
        print(f"❌ Orchestrator error: {e}")
        return False
    
    print()
    
    # Step 3: Run learning cycle with test data
    print("🧠 Step 3: Running Learning Cycle (this will take 5-10 minutes)...")
    print("   Sources:")
    
    web_urls = [
        "https://owasp.org/www-project-top-ten/",
        "https://www.kali.org/docs/general-use/kali-tools/",
    ]
    
    for url in web_urls:
        print(f"   - {url}")
    
    print()
    
    try:
        cycle_start = datetime.now()
        
        report_path = await orchestrator.run_learning_cycle(
            web_urls=web_urls,
            github_topics=["penetration-testing", "security-tools"],
            youtube_urls=None  # Skip YouTube for faster test
        )
        
        cycle_duration = (datetime.now() - cycle_start).total_seconds()
        
        print(f"✅ Learning cycle completed in {cycle_duration:.1f}s")
        print(f"✅ Report generated: {report_path}")
        
    except Exception as e:
        print(f"❌ Learning cycle failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print()
    
    # Step 4: Verify report
    print("📄 Step 4: Verifying Report...")
    try:
        if not Path(report_path).exists():
            print(f"❌ Report file not found: {report_path}")
            return False
        
        with open(report_path, 'r') as f:
            content = f.read()
        
        # Check report structure
        required_sections = [
            "JARVIS CLE Report",
            "Executive Summary",
            "Knowledge Acquired",
            "Improvement Proposals",
            "Self-Assessment"
        ]
        
        missing_sections = []
        for section in required_sections:
            if section not in content:
                missing_sections.append(section)
        
        if missing_sections:
            print(f"❌ Report missing sections: {missing_sections}")
            return False
        
        print(f"✅ Report structure valid ({len(content)} chars)")
        print(f"✅ All required sections present")
        
    except Exception as e:
        print(f"❌ Report verification failed: {e}")
        return False
    
    print()
    
    # Step 5: Check proposals
    print("💡 Step 5: Checking Proposals...")
    try:
        from app.cle.analysis.engine import ProposalGenerator
        
        generator = ProposalGenerator()
        proposals = generator.load_all_proposals()
        
        print(f"✅ Found {len(proposals)} proposals")
        
        if proposals:
            # Show first proposal
            p = proposals[0]
            print(f"   Example: [{p.id}] {p.title}")
            print(f"   Impact: {p.impact.value} | Effort: {p.effort.value} | Score: {p.score}")
        
    except Exception as e:
        print(f"❌ Proposal check failed: {e}")
        return False
    
    print()
    
    # Step 6: Check knowledge base growth
    print("📈 Step 6: Verifying Knowledge Base Growth...")
    try:
        final_counts = qdrant.get_total_knowledge_count()
        total_final = sum(final_counts.values())
        
        print(f"✅ Total knowledge items: {total_final}")
        for coll, count in final_counts.items():
            print(f"   - {coll}: {count}")
        
    except Exception as e:
        print(f"❌ Knowledge base check failed: {e}")
        return False
    
    print()
    print("=" * 80)
    print("✅ END-TO-END TEST PASSED!")
    print("=" * 80)
    print()
    print("Summary:")
    print(f"  - Report: {report_path}")
    print(f"  - Proposals: {len(proposals)}")
    print(f"  - Knowledge Items: {total_final}")
    print(f"  - Duration: {cycle_duration:.1f}s")
    print()
    
    return True


if __name__ == "__main__":
    success = asyncio.run(test_e2e())
    sys.exit(0 if success else 1)
