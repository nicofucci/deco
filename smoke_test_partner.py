
import requests
import sys

BASE_URL_PARTNER = "http://localhost:3007"
BASE_URL_API = "http://localhost:18001"
API_KEY = "pt_test_key_123" # From previous step
CLIENT_ID = "656252a8-93c0-439e-a05f-448783e4c96c" # iMac Client

def check(url, headers=None, expected_status=200):
    try:
        resp = requests.get(url, headers=headers, timeout=5)
        print(f"GET {url} -> {resp.status_code}")
        if resp.status_code == expected_status:
            return True
        else:
            print(f"FAIL: Expected {expected_status}, got {resp.status_code}")
            return False
    except Exception as e:
        print(f"FAIL: {e}")
        return False

print("=== SMOKE TEST: Partner Console API Routing ===")

# 1. Backend Health
print("\n[A] Backend Health")
check(f"{BASE_URL_API}/api/health")

# 2. Partner Proxy Health (via UI) 
# Note: Next.js Proxy requires path matching. /api/proxy/api/health -> /api/health
print("\n[B] Partner Proxy (Direct)")
check(f"{BASE_URL_PARTNER}/api/proxy/api/health")

# 3. Client Summary (via Proxy)
print("\n[C] Client Summary (Proxy + Auth)")
headers = {"X-Partner-API-Key": API_KEY}
check(f"{BASE_URL_PARTNER}/api/proxy/api/partners/me/clients/{CLIENT_ID}/summary", headers, 200)

# 4. Network Assets (via Proxy)
print("\n[D] Network Assets (Proxy + Auth)")
check(f"{BASE_URL_PARTNER}/api/proxy/api/network/clients/{CLIENT_ID}/network-assets", headers, 200)

# 5. Fleet (via Proxy)
print("\n[E] Fleet (Proxy + Auth)")
check(f"{BASE_URL_PARTNER}/api/proxy/api/fleet/clients/{CLIENT_ID}/agents", headers, 200)

# 6. Auth Check (Invalid Key)
print("\n[F] Auth Check (Invalid Key)")
check(f"{BASE_URL_PARTNER}/api/proxy/api/partners/me/clients/{CLIENT_ID}/summary", {"X-Partner-API-Key": "invalid"}, 401)

print("\n=== End Smoke Test ===")
