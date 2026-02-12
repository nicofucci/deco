import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_client_from_api_key
from app.models.domain import ScanJob, Agent, Client
from app.schemas.contracts import ScanResultUpload, ScanResultResponse
from app.services.result_dispatcher import persist_result_and_update_job

logger = logging.getLogger("DecoOrchestrator.ResultsAPI")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

router = APIRouter()


@router.post(
    "",
    response_model=ScanResultResponse,
    status_code=status.HTTP_201_CREATED,
)
def upload_scan_result(
    payload: ScanResultUpload,
    db: Session = Depends(get_db),
    client: Client = Depends(get_client_from_api_key),
):
    """
    El agente sube el resultado de un ScanJob.

    Flujo:
    - Verifica que el job exista y pertenezca al cliente.
    - Verifica que el agente exista y pertenezca al cliente.
    - Crea un ScanResult.
    - Actualiza el estado del job a 'done'.
    """
    job = (
        db.query(ScanJob)
        .filter(
            ScanJob.id == payload.scan_job_id,
            ScanJob.client_id == client.id,
        )
        .first()
    )
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ScanJob no encontrado para este cliente",
        )

    agent = (
        db.query(Agent)
        .filter(
            Agent.id == payload.agent_id,
            Agent.client_id == client.id,
        )
        .first()
    )
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agente no encontrado para este cliente",
        )

    logger.info(
        f"[RESULT] Recibido resultado para job {job.id} del agente {agent.id} "
        f"({job.type})"
    )

    # Normalizamos el raw_data con mínimos para trazabilidad
    raw_data = payload.raw_data or {}
    raw_data.setdefault("target", job.target)
    raw_data.setdefault("job_type", job.type)
    raw_data.setdefault("agent_id", agent.id)

    result = persist_result_and_update_job(
        db=db,
        job=job,
        agent=agent,
        raw_data=raw_data,
        summary=payload.summary or {},
        job_status="done",
    )

    return ScanResultResponse(
        status="accepted",
        received_at=result.created_at,
    )
