import aiohttp
from typing import Dict, Any, List

class CveSearchAgent:
    """Agente para buscar información sobre CVEs y vulnerabilidades."""
    
    def __init__(self):
        self.base_url = "https://cve.circl.lu/api/cve/" # Public API, no key required

    async def search_cve(self, cve_id: str) -> Dict[str, Any]:
        """Busca detalles de un CVE específico."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}{cve_id}") as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "id": data.get("id"),
                            "summary": data.get("summary"),
                            "cvss": data.get("cvss"),
                            "references": data.get("references", [])[:3]
                        }
                    else:
                        return {"error": f"CVE not found or API error: {response.status}"}
        except Exception as e:
            return {"error": str(e)}

    async def search_product(self, vendor: str, product: str) -> List[Dict[str, Any]]:
        """Busca vulnerabilidades por producto (Simulado por ahora para no saturar API)."""
        # En una implementación real, usaríamos la API de búsqueda de cve.circl.lu o NVD
        return [
            {"id": "CVE-2023-1234", "summary": f"Vulnerabilidad simulada en {vendor} {product}", "cvss": 9.8},
            {"id": "CVE-2023-5678", "summary": f"Otra vulnerabilidad en {vendor} {product}", "cvss": 7.5}
        ]

cve_agent = CveSearchAgent()
