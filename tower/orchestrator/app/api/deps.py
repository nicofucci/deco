from typing import Generator, Optional

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.session import SessionLocal
from app.models.domain import Client


def get_db() -> Generator[Session, None, None]:
    """
    Dependencia para obtener una sesión de base de datos.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_client_from_api_key(
    db: Session = Depends(get_db),
    api_key: Optional[str] = Header(default=None, alias="x-client-api-key"),
    authorization: Optional[str] = Header(default=None),
) -> Client:
    """
    Obtiene el cliente a partir del header X-Client-API-Key (Agent API Key)
    O del header Authorization: Bearer <token> (si el agente lo envía).
    Si no es válido, lanza 401.
    """
    token_key = None
    if authorization:
        scheme, _, param = authorization.partition(" ")
        if scheme.lower() == "bearer":
            token_key = param

    final_key = api_key or token_key

    if not final_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Falta cabecera X-Client-API-Key o Authorization",
        )

    # Check agent_api_key first
    client = db.query(Client).filter(Client.agent_api_key == final_key).first()
    
    # Fallback to client_panel_api_key (just in case)
    if not client:
        client = db.query(Client).filter(Client.client_panel_api_key == final_key).first()

    # Auto-Registration Logic (Lab Mode)
    if not client:
        # Create a new client automatically
        new_client_name = f"Auto-Client-{final_key[:8]}"
        client = Client(
            name=new_client_name,
            agent_api_key=final_key,
            status="active"
        )
        db.add(client)
        db.commit()
        db.refresh(client)
        
    if client.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cliente no está activo",
        )

    return client

def get_client_from_panel_key(
    db: Session = Depends(get_db),
    api_key: Optional[str] = Header(default=None, alias="x-client-api-key"),
) -> Client:
    """
    Obtiene el cliente a partir del header X-Client-API-Key (Client Panel API Key).
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Falta cabecera X-Client-API-Key",
        )

    client = db.query(Client).filter(Client.client_panel_api_key == api_key).first()
    
    # Fallback
    if not client:
        client = db.query(Client).filter(Client.agent_api_key == api_key).first()

    if not client:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key de panel inválida",
        )

    if client.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cliente no está activo",
        )

    return client


import os

ADMIN_MASTER_KEY = os.getenv("DECO_ADMIN_MASTER_KEY", "")

def verify_admin_master_key(
    master_key: str = Header(..., alias="X-Admin-Master-Key")
):
    print(f"DEBUG: EXPECTED={ADMIN_MASTER_KEY} RECEIVED={master_key}")
    """
    Verifica que la clave maestra de administrador sea correcta.
    """
    if not ADMIN_MASTER_KEY or master_key != ADMIN_MASTER_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin master key inválida",
        )
    return True

verify_master_key = verify_admin_master_key

from app.models.domain import Partner, PartnerAPIKey

def get_current_partner_from_token(
    db: Session = Depends(get_db),
    # En una implementación real usaríamos OAuth2PasswordBearer y validaríamos JWT
    # Para este MVP, simularemos que el token es "partner_id:secret" o simplemente el ID si simplificamos
    authorization: Optional[str] = Header(default=None)
) -> Partner:
    """
    Valida el token Bearer del Partner.
    Formato esperado: Authorization: Bearer <partner_id> (SIMPLIFICADO para MVP)
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    
    scheme, _, param = authorization.partition(" ")
    if scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid auth scheme")
    
    partner_id = param # En prod: decode_jwt(param)
    
    partner = db.query(Partner).filter(Partner.id == partner_id).first()
    if not partner:
        raise HTTPException(status_code=401, detail="Invalid partner token")
        
    if partner.status != "active":
        raise HTTPException(status_code=403, detail="Partner suspended")
        
    return partner

def get_partner_from_api_key(
    db: Session = Depends(get_db),
    api_key: Optional[str] = Header(default=None, alias="X-Partner-API-Key")
) -> Partner:
    """
    Obtiene el partner via API Key programática.
    """
    if not api_key:
        raise HTTPException(status_code=401, detail="Missing X-Partner-API-Key")
        
    # Check direct Partner key first
    partner = db.query(Partner).filter(Partner.partner_api_key == api_key).first()
    
    if partner:
        if partner.status != "active":
            raise HTTPException(status_code=403, detail="Partner suspended")
        return partner

    # Fallback to PartnerAPIKey table
    key_record = db.query(PartnerAPIKey).filter(PartnerAPIKey.api_key == api_key).first()
    if not key_record:
        raise HTTPException(status_code=401, detail="Invalid Partner API Key")
        
    if not key_record.active:
        raise HTTPException(status_code=403, detail="API Key inactive")
        
    # Update usage
    key_record.last_used_at = func.now()
    db.commit()
    
    if key_record.partner.status != "active":
        raise HTTPException(status_code=403, detail="Partner suspended")
        
    return key_record.partner
