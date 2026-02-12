import requests
import json
import sys
from datetime import datetime

API_URL = "http://127.0.0.1:8000"

def run_tests():
    print(f"\n=== Smoke Tests Agentes IA ===")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Endpoint: {API_URL}/ai/tests/run-sequence\n")

    try:
        response = requests.post(f"{API_URL}/ai/tests/run-sequence")
        response.raise_for_status()
        data = response.json()
        
        results = data.get("results", [])
        
        ok_count = 0
        skipped_count = 0
        error_count = 0
        
        for res in results:
            status = res.get("status")
            key = res.get("key")
            duration = res.get("duration_ms")
            summary = res.get("summary")
            
            if status == "ok":
                symbol = "✔"
                ok_count += 1
            elif status == "skipped":
                symbol = "✖" # Using X for skipped/disabled as per prompt example style
                skipped_count += 1
            else:
                symbol = "✖"
                error_count += 1
                
            print(f"{symbol} {key:<20} ({duration:>4} ms) -> {status.upper()} – {summary}")

        print("\n===============================")
        print(f"Resultado global: {ok_count} OK, {skipped_count} SKIPPED, {error_count} ERROR")
        
    except requests.exceptions.ConnectionError:
        print("ERROR: No se pudo conectar a la API. Asegúrate de que Jarvis API esté corriendo en el puerto 8000.")
    except Exception as e:
        print(f"ERROR: Falló la ejecución de pruebas: {e}")

if __name__ == "__main__":
    run_tests()
