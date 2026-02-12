from fastapi import APIRouter, Depends, Request
from app.api.routers.agents import agent_heartbeat, register_agent
from app.schemas.contracts import AgentRegisterRequest, HeartbeatRequest
from app.api.deps import get_db, get_client_from_api_key
from sqlalchemy.orm import Session
from app.models.domain import Client

router = APIRouter()

@router.post("/heartbeat")
def legacy_heartbeat(
    payload: HeartbeatRequest,
    db: Session = Depends(get_db),
    client: Client = Depends(get_client_from_api_key),
):
    return agent_heartbeat(payload, db, client)

@router.post("/register")
def legacy_register(
    payload: AgentRegisterRequest,
    db: Session = Depends(get_db),
    client: Client = Depends(get_client_from_api_key),
):
    return register_agent(payload, db, client)
