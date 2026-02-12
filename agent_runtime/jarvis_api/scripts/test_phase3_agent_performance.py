import requests
import sys
from datetime import datetime

# Usamos el puerto 8000 (Jarvis API) directamente para probar la lógica base
# O el puerto 8000 (Orchestrator API container) para probar la integración completa
API_URL = "http://127.0.0.1:8000"
PROXY_URL = "http://orchestrator_api:8000"

def test_endpoint(url, description):
    print(f"Testing {description} ({url})...", end=" ")
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print("OK")
            return response.json()
        else:
            print(f"FAIL (Status {response.status_code})")
            print(response.text)
            return None
    except Exception as e:
        print(f"FAIL (Exception: {e})")
        return None

def run_tests():
    print(f"\n=== QA Phase 3: Agent Performance Dashboard ===")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # 1. Test Summary (Jarvis API)
    summary = test_endpoint(f"{API_URL}/ai/performance/summary", "Jarvis API Summary")
    if summary:
        agents = summary.get("agents", [])
        print(f"  -> Found {len(agents)} agents in summary.")
        if len(agents) > 0:
            print(f"  -> Sample agent: {agents[0]['agent_key']} (Status: {agents[0]['status']})")

    # 2. Test History (Jarvis API)
    if summary and len(summary.get("agents", [])) > 0:
        agent_key = summary["agents"][0]["agent_key"]
        history = test_endpoint(f"{API_URL}/ai/performance/history/{agent_key}", f"Jarvis API History for {agent_key}")
        if history:
            runs = history.get("history", [])
            print(f"  -> Found {len(runs)} historical runs.")

    # 3. Test Ranking (Jarvis API)
    ranking = test_endpoint(f"{API_URL}/ai/performance/ranking", "Jarvis API Ranking")
    if ranking:
        print(f"  -> Top agent: {ranking[0]['agent_key']} (Score: {ranking[0].get('ranking_score')})")

    print("\n--- Integration Tests (Orchestrator Proxy) ---")
    
    # 4. Test Proxy Summary
    proxy_summary = test_endpoint(f"{PROXY_URL}/ai/performance/summary", "Orchestrator Proxy Summary")
    if proxy_summary:
        print("  -> Proxy seems to be working correctly.")

if __name__ == "__main__":
    run_tests()
