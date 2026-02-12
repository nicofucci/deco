from typing import List
import secrets

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_client_from_api_key, get_client_from_panel_key
from app.models.domain import Client
from app.schemas.contracts import ClientCreate, ClientRead

router = APIRouter()


def generate_api_key() -> str:
    """
    Genera una API key segura para el cliente.
    """
    return secrets.token_hex(8)


@router.post(
    "",
    response_model=ClientRead,
    status_code=status.HTTP_201_CREATED,
)
def create_client(
    payload: ClientCreate,
    db: Session = Depends(get_db),
):
    """
    Crea un nuevo cliente con una API key única.
    """
    api_key = generate_api_key()

    client = Client(
        name=payload.name,
        contact_email=payload.contact_email,
        api_key=api_key,
        client_panel_api_key=api_key,
        agent_api_key=secrets.token_hex(16),
        status="active",
    )
    db.add(client)
    db.commit()
    db.refresh(client)

    return client


@router.get(
    "/me",
    response_model=ClientRead,
    summary="Devuelve información del cliente autenticado",
)
def get_me(client: Client = Depends(get_client_from_panel_key)):
    """
    Devuelve los datos del cliente asociado a la API Key enviada en el header:
    X-Client-API-Key: <api_key_del_cliente>
    """
    return client


@router.get(
    "/me/agents",
    summary="Lista los agentes del cliente autenticado",
)
def get_my_agents(
    db: Session = Depends(get_db),
    client: Client = Depends(get_client_from_panel_key),
):
    """
    Devuelve la lista de agentes asociados al cliente.
    """
    agents = db.query(Client).filter(Client.id == client.id).first().agents
    
    # Sort by created_at desc
    agents.sort(key=lambda x: x.created_at, reverse=True)

    return [
        {
            "id": a.id,
            "hostname": a.hostname,
            "status": a.status,
            "last_seen_at": a.last_seen_at,
            "local_ip": a.local_ip,
            "primary_cidr": a.primary_cidr,
            "interfaces": a.interfaces,
            "created_at": a.created_at,
        }
        for a in agents
    ]


@router.get(
    "",
    response_model=List[ClientRead],
)
def list_clients(
    db: Session = Depends(get_db),
):
    """
    Lista todos los clientes registrados.
    (Más adelante podremos filtrar, paginar, etc.)
    """
    clients = db.query(Client).order_by(Client.created_at.desc()).all()
    return clients


@router.get(
    "/{client_id}",
    response_model=ClientRead,
)
def get_client(
    client_id: str,
    db: Session = Depends(get_db),
):
    """
    Devuelve un cliente por ID.
    """
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente no encontrado",
        )
    return client


@router.patch(
    "/{client_id}/status/{new_status}",
    response_model=ClientRead,
)
def update_client_status(
    client_id: str,
    new_status: str,
    db: Session = Depends(get_db),
):
    """
    Actualiza el estado del cliente (active / suspended).
    """
    if new_status not in ("active", "suspended"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Estado inválido. Usa 'active' o 'suspended'.",
        )

    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente no encontrado",
        )

    client.status = new_status
    db.commit()
    db.refresh(client)

    return client
