from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any
from app.agents.specialized.cve_agent import cve_agent

router = APIRouter()

@router.get("/cve/{cve_id}")
async def get_cve_details(cve_id: str):
    """Obtiene detalles de un CVE específico."""
    result = await cve_agent.search_cve(cve_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

@router.get("/search")
async def search_vulnerabilities(query: str = Query(..., min_length=3)):
    """Busca vulnerabilidades por producto o palabra clave (Simulado)."""
    # En el futuro esto parsearía el query para extraer vendor/product
    # Por ahora asumimos que el query es el nombre del producto
    results = await cve_agent.search_product("generic", query)
    return results
