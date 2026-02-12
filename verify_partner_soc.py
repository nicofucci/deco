import requests
import json
import uuid

API_URL = "http://127.0.0.1:18001"
ADMIN_KEY = "deco-admin-master-key-123" # Adjust if needed, or use existing key from DB

def test_partner_flow():
    print("=== INICIANDO TEST PARTNER SOC ===")
    
    # 1. Create Partner
    partner_email = f"partner_{uuid.uuid4().hex[:8]}@test.com"
    print(f"Creating Partner: {partner_email}")
    # Assuming we have an admin endpoint or we use the public registration if available, 
    # but partners are usually created by admin. 
    # Let's try to login with a known partner or create one via DB script if API is protected.
    # For this test, let's assume we can use the partner creation endpoint if it's open or we have a key.
    # Actually, partners.py has create_partner but it might need auth or be open.
    # Let's try to create one.
    
    res = requests.post(f"{API_URL}/api/partners/", json={
        "email": partner_email,
        "password": "password123",
        "name": "Test Partner"
    })
    
    if res.status_code != 200:
        print(f"Failed to create partner: {res.text}")
        # Try login if exists
    
    # Login
    res = requests.post(f"{API_URL}/api/partners/login", json={
        "email": partner_email,
        "password": "password123"
    })
    if res.status_code != 200:
        print(f"Login failed: {res.text}")
        return
        
    token = res.json()["access_token"]
    partner_id = res.json()["partner_id"]
    print(f"Logged in. Token: {token}")
    
    headers = {"X-Partner-API-Key": token} # Using ID as token for MVP as per code
    
    # 2. Create Client
    client_name = f"Client_{uuid.uuid4().hex[:6]}"
    print(f"Creating Client: {client_name}")
    res = requests.post(f"{API_URL}/api/partners/me/clients", headers=headers, json={
        "name": client_name,
        "contact_email": f"contact_{uuid.uuid4().hex[:6]}@client.com"
    })
    if res.status_code != 200:
        print(f"Failed to create client: {res.text}")
        return
    
    client_id = res.json()["id"]
    print(f"Client Created: {client_id}")
    
    # 3. Create Agent (Mocked via DB or just assume one exists if we could)
    # Since we can't easily create an agent via API without the agent flow, 
    # let's try to run a scan. The code handles "no agent" by erroring or fallback.
    # Let's see if we can create an agent via a backdoor or just expect the error "No agents available" which confirms the endpoint works.
    
    print("Testing Remote Scan (Expect 400 if no agents)...")
    res = requests.post(f"{API_URL}/api/partners/me/clients/{client_id}/scan", headers=headers, json={
        "type": "quick"
    })
    print(f"Scan Response: {res.status_code} - {res.text}")
    
    if res.status_code == 400 and "No hay agentes" in res.text:
        print("SUCCESS: Endpoint reached and validated agent requirement.")
    elif res.status_code == 200:
        print("SUCCESS: Scan job created.")
    else:
        print("FAILURE: Unexpected response.")

    # 4. Test Reports
    print("Testing Report Generation...")
    res = requests.post(f"{API_URL}/api/partners/me/clients/{client_id}/reports", headers=headers, json={
        "type": "executive"
    })
    print(f"Report Response: {res.status_code} - {res.text}")
    
    if res.status_code == 200:
        print("SUCCESS: Report generation triggered.")
    else:
        print("FAILURE: Report generation failed.")

if __name__ == "__main__":
    test_partner_flow()
