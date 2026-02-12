import requests
import os
import json

API_URL = "http://localhost:19001"
MASTER_KEY = "MASTER_DECO"
HEADERS = {"X-Admin-Master-Key": MASTER_KEY}

def list_keys():
    try:
        res = requests.get(f"{API_URL}/api/admin/clients", headers=HEADERS)
        if res.status_code != 200:
            print(f"Failed: {res.text}")
            return
        
        clients = res.json()
        print(f"Found {len(clients)} clients:")
        for c in clients:
            # We need to fetch details to see keys? Admin list might not show secrets.
            # But wait, the admin list endpoint in admin.py doesn't return api_key.
            # We need to query the DB directly or use a different endpoint.
            pass
            
    except Exception as e:
        print(f"Error: {e}")

# Direct DB query
from app.db.session import SessionLocal
from app.models.domain import Client

def dump_keys():
    db = SessionLocal()
    clients = db.query(Client).all()
    print("\n--- CLIENT API KEYS ---")
    for c in clients:
        print(f"Client: {c.name}")
        print(f"  ID: {c.id}")
        print(f"  Agent Key: {c.agent_api_key}")
        print(f"  Panel Key: {c.client_panel_api_key}")
        print(f"  Legacy Key: {c.api_key}")
        print("-" * 30)
    db.close()

if __name__ == "__main__":
    dump_keys()
