import requests
import argparse
import sys
from datetime import datetime

import os

API_URL = os.getenv("JARVIS_API_URL", "http://127.0.0.1:8000")

def run_benchmarks(agent_key: str, runs: int):
    print(f"\n=== Benchmarks Agentes IA ===")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Endpoint: {API_URL}/ai/tests/benchmark\n")

    payload = {
        "agent_key": agent_key,
        "runs": runs
    }

    try:
        response = requests.post(f"{API_URL}/ai/tests/benchmark", json=payload)
        response.raise_for_status()
        data = response.json()
        
        results = data.get("results", [])
        
        print(f"{'Agente':<20} {'Versión':<10} {'Éxito':<10} {'Latencia media':<15} {'Score medio':<10}")
        print("-" * 70)
        
        ok_count = 0
        
        for res in results:
            key = res.get("agent_key")
            ver = res.get("version")
            rate = res.get("success_rate")
            runs_done = res.get("runs")
            lat = res.get("avg_latency_ms")
            score = res.get("avg_score")
            
            success_str = f"{int(rate * runs_done)}/{runs_done}"
            
            print(f"{key:<20} {ver:<10} {success_str:<10} {lat:<15} {score:<10}")
            
            if rate == 1.0:
                ok_count += 1
                
        print("\n" + "=" * 30)
        print(f"Resultado global: {ok_count} agentes OK")

    except requests.exceptions.ConnectionError:
        print("ERROR: No se pudo conectar a la API. Asegúrate de que Jarvis API esté corriendo.")
    except Exception as e:
        print(f"ERROR: Falló la ejecución de benchmarks: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ejecutar benchmarks de Agentes IA")
    parser.add_argument("--all", action="store_true", help="Ejecutar para todos los agentes")
    parser.add_argument("--agent", type=str, help="Key del agente específico")
    parser.add_argument("--runs", type=int, default=3, help="Número de ejecuciones por agente")
    
    args = parser.parse_args()
    
    if args.all:
        run_benchmarks("ALL", args.runs)
    elif args.agent:
        run_benchmarks(args.agent, args.runs)
    else:
        print("Debes especificar --all o --agent <key>")
