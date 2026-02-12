import requests
import os
import time

API_URL = "http://localhost:19001"
MASTER_KEY = "DECO-231908!@"
HEADERS = {"X-Admin-Master-Key": MASTER_KEY}

def delete_all_clients():
    print("Fetching clients...")
    try:
        res = requests.get(f"{API_URL}/api/admin/clients", headers=HEADERS)
        if res.status_code != 200:
            print(f"Failed to fetch clients: {res.text}")
            return
        
        clients = res.json()
        print(f"Found {len(clients)} clients.")
        
        for client in clients:
            print(f"Deleting client {client['name']} ({client['id']})...")
            del_res = requests.delete(f"{API_URL}/api/admin/clients/{client['id']}", headers=HEADERS)
            if del_res.status_code == 200:
                print("  Deleted.")
            else:
                print(f"  Failed: {del_res.text}")
    except Exception as e:
        print(f"Error: {e}")

def delete_all_partners():
    print("\nFetching partners...")
    try:
        res = requests.get(f"{API_URL}/api/admin/partners", headers=HEADERS)
        if res.status_code != 200:
            print(f"Failed to fetch partners: {res.text}")
            return
        
        partners = res.json()
        print(f"Found {len(partners)} partners.")
        
        for partner in partners:
            print(f"Deleting partner {partner['name']} ({partner['id']})...")
            del_res = requests.delete(f"{API_URL}/api/admin/partners/{partner['id']}", headers=HEADERS)
            if del_res.status_code == 200:
                print("  Deleted.")
            else:
                print(f"  Failed: {del_res.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Starting cleanup...")
    delete_all_clients()
    delete_all_partners()
    print("Cleanup complete.")
