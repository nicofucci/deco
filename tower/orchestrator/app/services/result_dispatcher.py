import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.models.domain import Agent, ScanJob, ScanResult
from app.services.processor import process_scan_result

logger = logging.getLogger("DecoOrchestrator.Results")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def _enqueue_processing(result_id: str):
    """
    Encola el procesamiento asíncrono del resultado en Redis.
    Si falla, intenta procesar sincrónicamente para no perder el evento.
    """
    # FORCE SYNC PROCESSING (No worker service available yet)
    try:
        logger.info(f"[RESULT_DISPATCH] Procesando resultado {result_id} sincrónicamente (Worker no disponible)")
        process_scan_result(result_id)
    except Exception as e:
        logger.error(f"[RESULT_DISPATCH] Error procesando resultado {result_id}: {e}")
    return

    # OLD ASYNC LOGIC (Disabled until worker is added)
    # try:
    #     from redis import Redis
    #     from rq import Queue
    # ...


def persist_result_and_update_job(
    db: Session,
    job: ScanJob,
    agent: Agent,
    raw_data: Dict[str, Any],
    summary: Optional[Dict[str, Any]],
    job_status: str,
) -> ScanResult:
    """
    Guarda/actualiza el ScanResult y deja el job en el estado final indicado.
    - Marca timestamps started/finished si no estaban.
    - Reasigna agent_id si el job venía sin agente (para trazabilidad).
    - Encola el procesamiento (assets/findings).
    """
    now = datetime.now(timezone.utc)

    if job.started_at is None:
        job.started_at = now
    job.finished_at = now
    job.status = job_status
    if job.agent_id is None:
        job.agent_id = agent.id

    result = job.results
    if result:
        # Actualizamos el resultado existente para reintentos
        result.raw_data = raw_data
        result.parsed_summary = summary
        result.created_at = now
    else:
        result = ScanResult(
            scan_job_id=job.id,
            raw_data=raw_data,
            parsed_summary=summary,
            created_at=now,
        )
        db.add(result)

    db.commit()
    db.refresh(result)

    _enqueue_processing(result.id)

    return result
