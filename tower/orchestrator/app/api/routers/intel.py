from fastapi import APIRouter, Depends, HTTPException
from app.api.deps import verify_master_key
from app.services.threat_intel import threat_intel_service
from app.services.cache import cache_service

router = APIRouter(
    prefix="/api/intel",
    tags=["intel"],
    dependencies=[Depends(verify_master_key)]
)

@router.get("/ip/{ip_address}")
@cache_service.cache(expire=3600) # Cache for 1 hour
def get_ip_reputation(ip_address: str):
    """
    Obtiene la reputación de una IP desde el servicio de Threat Intelligence.
    """
    return threat_intel_service.get_ip_reputation(ip_address)
