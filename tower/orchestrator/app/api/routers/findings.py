from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime

from app.api.deps import get_db, get_client_from_api_key
from app.models.domain import Finding, Client, Asset

router = APIRouter()

class FindingResponse(BaseModel):
    id: str
    asset_id: str
    severity: str
    title: str
    description: Optional[str]
    recommendation: Optional[str]
    detected_at: datetime

    class Config:
        from_attributes = True

@router.get(
    "",
    response_model=List[FindingResponse],
    status_code=status.HTTP_200_OK,
)
def list_findings(
    asset_id: Optional[str] = None,
    db: Session = Depends(get_db),
    client: Client = Depends(get_client_from_api_key),
):
    """
    Lista todos los findings del cliente.
    Si se especifica asset_id, filtra por ese activo.
    """
    query = db.query(Finding).filter(Finding.client_id == client.id)

    if asset_id:
        # Verificar que el asset pertenezca al cliente
        asset = db.query(Asset).filter(Asset.id == asset_id, Asset.client_id == client.id).first()
        if not asset:
            raise HTTPException(status_code=404, detail="Asset not found")
        query = query.filter(Finding.asset_id == asset_id)

    findings = query.all()
    return findings

@router.get(
    "/{asset_id}",
    response_model=List[FindingResponse],
    status_code=status.HTTP_200_OK,
)
def list_findings_by_asset(
    asset_id: str,
    db: Session = Depends(get_db),
    client: Client = Depends(get_client_from_api_key),
):
    """
    Endpoint específico para listar findings de un asset.
    (Redundante con el filtro anterior, pero solicitado explícitamente)
    """
    # Verificar que el asset pertenezca al cliente
    asset = db.query(Asset).filter(Asset.id == asset_id, Asset.client_id == client.id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    findings = db.query(Finding).filter(
        Finding.client_id == client.id,
        Finding.asset_id == asset_id
    ).all()
    
    return findings
