import sys
import logging
logging.basicConfig(level=logging.INFO)
sys.path.append("/app")
from app.db.session import SessionLocal
from app.models.domain import NetworkAsset
from app.services.enrichment import EnrichmentService

db = SessionLocal()
asset_id = "605d7819-394c-415f-bb98-979a50b7724b"
asset = db.query(NetworkAsset).filter(NetworkAsset.id == asset_id).first()
if not asset:
    print("Asset not found! Finding by IP...")
    asset = db.query(NetworkAsset).filter(NetworkAsset.ip == "192.168.100.200").first()

if not asset:
    print("Asset still not found.")
    sys.exit(1)

print(f"Enriching asset {asset.hostname} ({asset.ip})...")
service = EnrichmentService(db)
count = service.process_asset(asset)
print(f"Persisted {count} vulnerabilities.")
