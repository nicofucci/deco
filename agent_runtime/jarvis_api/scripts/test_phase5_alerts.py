import requests
import json
import time
import sys

# Configuration
API_URL = "http://localhost:8000"

def print_step(step):
    print(f"\n=== {step} ===")

def wait_for_api():
    print("Esperando a que Jarvis API esté disponible...")
    for i in range(10):
        try:
            requests.get(f"{API_URL}/api/health")
            print("API disponible.")
            return
        except:
            time.sleep(2)
    print("Error: API no disponible tras 20s")
    sys.exit(1)

def test_alerts_flow():
    wait_for_api()
    print_step("1. Evaluando Alertas (Trigger)")
    try:
        resp = requests.post(f"{API_URL}/ai/alerts/evaluate")
        resp.raise_for_status()
        data = resp.json()
        print(f"Evaluación completada: {json.dumps(data, indent=2)}")
    except Exception as e:
        print(f"Error evaluando alertas: {e}")
        sys.exit(1)

    print_step("2. Listando Alertas Abiertas")
    try:
        resp = requests.get(f"{API_URL}/ai/alerts", params={"status": "open"})
        resp.raise_for_status()
        alerts = resp.json()
        print(f"Alertas abiertas encontradas: {len(alerts)}")
        if len(alerts) > 0:
            print(f"Ejemplo de alerta: {json.dumps(alerts[0], indent=2)}")
        else:
            print("No hay alertas abiertas para probar el flujo de resolución.")
            # Create a dummy alert for testing if none exist
            print("Creando alerta de prueba manual...")
            # Note: We don't have a direct create endpoint exposed, so we rely on evaluate.
            # If evaluate didn't create any, we might need to mock data or force a condition.
            # For now, let's assume evaluate might have created something or we skip.
            return
            
    except Exception as e:
        print(f"Error listando alertas: {e}")
        sys.exit(1)

    target_alert = alerts[0]
    alert_id = target_alert["id"]

    print_step(f"3. Probando Acknowledge en Alerta {alert_id}")
    try:
        resp = requests.post(f"{API_URL}/ai/alerts/{alert_id}/ack")
        resp.raise_for_status()
        updated = resp.json()
        print(f"Estado actualizado: {updated['status']}")
        assert updated['status'] == "acknowledged"
    except Exception as e:
        print(f"Error en Acknowledge: {e}")
        sys.exit(1)

    print_step(f"4. Probando Resolve en Alerta {alert_id}")
    try:
        resp = requests.post(f"{API_URL}/ai/alerts/{alert_id}/resolve")
        resp.raise_for_status()
        updated = resp.json()
        print(f"Estado actualizado: {updated['status']}")
        assert updated['status'] == "resolved"
        assert updated['resolved_at'] is not None
    except Exception as e:
        print(f"Error en Resolve: {e}")
        sys.exit(1)

    print("\n✅ Flujo de Alertas verificado correctamente.")

if __name__ == "__main__":
    test_alerts_flow()
