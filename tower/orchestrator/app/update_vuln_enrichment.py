from app.db.session import engine
from app.models.domain import Base, NetworkVulnerability

def run_migration():
    print("[*] Applying Vulnerability Enrichment Migration...")
    try:
        # Create table network_vulnerabilities
        NetworkVulnerability.__table__.create(bind=engine, checkfirst=True)
        print("[+] Table 'network_vulnerabilities' created successfully.")
    except Exception as e:
        print(f"[-] Migration failed: {e}")

if __name__ == "__main__":
    run_migration()
