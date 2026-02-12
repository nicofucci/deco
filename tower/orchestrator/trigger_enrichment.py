import sys
import os
import logging

logging.basicConfig(level=logging.INFO)
sys.path.append("/app")

from app.db.session import SessionLocal
from app.services.enrichment import CVEEnricher

db = SessionLocal()
enricher = CVEEnricher(db)

# Test Fixed Windows CPE
test_cpe = "cpe:2.3:o:microsoft:windows_10:-:*:*:*:*:*:*:*"
print(f"Testing NVD lookup for: {test_cpe}")

results = enricher.search_cves([test_cpe])
print(f"Found {len(results)} vulnerabilities.")
