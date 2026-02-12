from typing import List, Optional
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_client_from_panel_key
from app.models.domain import ScanJob, Agent, Client
from app.schemas.contracts import ScanJobCreate, ScanJobResponse

router = APIRouter()

ALLOWED_JOB_TYPES = {"discovery", "ports"}  # valores canónicos que entiende el backend/agents
JOB_TYPE_ALIASES = {
    # Alias que vienen del frontend para compatibilidad con la UI
    "full": "ports",
    "full_scan": "ports",
}


def _normalize_job_type(job_type: str) -> str:
    """
    Devuelve el tipo canónico aceptado internamente.
    - Acepta alias como "full" y los convierte a "ports" para mantener compatibilidad.
    """
    normalized = (job_type or "").strip().lower()
    return JOB_TYPE_ALIASES.get(normalized, normalized)


def _select_agent_for_job(
    db: Session,
    client: Client,
    requested_agent_id: Optional[str],
) -> Optional[Agent]:
    """
    Selecciona el agente que ejecutará el job.
    - Si viene agent_id, verifica que pertenezca al cliente.
    - Si no viene, intenta elegir el primer agente online del cliente.
    - Puede devolver None (job quedará sin agente asignado hasta que un agente haga heartbeat).
    """
    if requested_agent_id:
        agent = (
            db.query(Agent)
            .filter(
                Agent.id == requested_agent_id,
                Agent.client_id == client.id,
            )
            .first()
        )
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agente especificado no encontrado para este cliente",
            )
        return agent

    # Sin agent_id: intentamos asignar automáticamente uno online
    agent = (
        db.query(Agent)
        .filter(
            Agent.client_id == client.id,
        )
        .order_by(Agent.created_at.asc())
        .first()
    )
    return agent


@router.post(
    "",
    response_model=ScanJobResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_scan_job(
    payload: ScanJobCreate,
    db: Session = Depends(get_db),
    client: Client = Depends(get_client_from_panel_key),
):
    """
    Crea un nuevo ScanJob para el cliente autenticado.

    Notas:
    - Ignoramos el client_id del payload y usamos el del token (cabecera X-Client-API-Key).
    - Si no se especifica agent_id, intentamos asignar uno automáticamente.
    - El job se crea en estado 'pending'.
    """
    normalized_type = _normalize_job_type(payload.type)

    if normalized_type not in ALLOWED_JOB_TYPES:
        accepted_types = sorted(ALLOWED_JOB_TYPES.union(JOB_TYPE_ALIASES.keys()))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de job inválido: '{payload.type}'. Usa uno de: {accepted_types}",
        )

    if not payload.target or not payload.target.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El campo 'target' es obligatorio",
        )

    agent = _select_agent_for_job(
        db=db,
        client=client,
        requested_agent_id=payload.agent_id,
    )

    job = ScanJob(
        client_id=client.id,
        agent_id=agent.id if agent else None,
        type=normalized_type,
        target=payload.target.strip(),
        status="pending",
        created_at=datetime.now(timezone.utc),
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    return job


@router.get(
    "",
    response_model=List[ScanJobResponse],
)
def list_scan_jobs(
    db: Session = Depends(get_db),
    client: Client = Depends(get_client_from_panel_key),
):
    """
    Lista todos los ScanJobs del cliente autenticado.
    """
    jobs = (
        db.query(ScanJob)
        .filter(ScanJob.client_id == client.id)
        .order_by(ScanJob.created_at.desc())
        .all()
    )
    return jobs


@router.get(
    "/{job_id}",
    response_model=ScanJobResponse,
)
def get_scan_job(
    job_id: str,
    db: Session = Depends(get_db),
    client: Client = Depends(get_client_from_panel_key),
):
    """
    Devuelve un ScanJob por ID (si pertenece al cliente).
    """
    job = (
        db.query(ScanJob)
        .filter(
            ScanJob.id == job_id,
            ScanJob.client_id == client.id,
        )
        .first()
    )

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ScanJob no encontrado para este cliente",
        )

    return job


@router.delete(
    "/{job_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_scan_job(
    job_id: str,
    db: Session = Depends(get_db),
    client: Client = Depends(get_client_from_panel_key),
):
    """
    Elimina un ScanJob por ID (si pertenece al cliente).
    """
    job = (
        db.query(ScanJob)
        .filter(
            ScanJob.id == job_id,
            ScanJob.client_id == client.id,
        )
        .first()
    )

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ScanJob no encontrado para este cliente",
        )

    db.delete(job)
    db.commit()
    return None
