import logging
import sys
import uuid
from typing import Optional

from sqlalchemy import inspect
from sqlalchemy.exc import OperationalError

from app.db.base import Base
from app.db.session import SessionLocal, engine

# Registrar todos los modelos en el metadata
import app.models.domain  # noqa: F401
import app.models.master_auth  # noqa: F401

logger = logging.getLogger("init_db")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)


def _ensure_demo_client(session) -> Optional[dict]:
    from app.models.domain import Client  # import diferido para evitar ciclos

    demo = session.query(Client).filter(Client.name == "Demo Client").first()
    if demo:
        return {
            "id": demo.id,
            "agent_api_key": demo.agent_api_key,
            "client_panel_api_key": demo.client_panel_api_key,
        }

    agent_key = f"client_{uuid.uuid4().hex}"
    panel_key = f"panel_{uuid.uuid4().hex}"

    demo = Client(
        name="Demo Client",
        status="active",
        agent_api_key=agent_key,
        client_panel_api_key=panel_key,
    )
    session.add(demo)
    session.commit()
    session.refresh(demo)
    return {
        "id": demo.id,
        "agent_api_key": demo.agent_api_key,
        "client_panel_api_key": demo.client_panel_api_key,
    }


def main() -> int:
    try:
        logger.info("Creando tablas declaradas en Base.metadata...")
        Base.metadata.create_all(bind=engine)
        inspector = inspect(engine)
        tables = sorted(inspector.get_table_names())
        logger.info("Tablas detectadas (%s): %s", len(tables), ", ".join(tables))
    except OperationalError as exc:
        logger.error("No se pudo conectar o crear tablas: %s", exc)
        return 1
    except Exception as exc:  # pragma: no cover
        logger.exception("Error inesperado creando tablas: %s", exc)
        return 1

    demo_info: Optional[dict] = None
    try:
        with SessionLocal() as session:
            demo_info = _ensure_demo_client(session)
    except OperationalError as exc:
        logger.error("No se pudo inicializar cliente demo: %s", exc)
        return 1
    except Exception as exc:  # pragma: no cover
        logger.exception("Error inesperado al crear cliente demo: %s", exc)
        return 1

    if demo_info:
        logger.info("Cliente demo listo: id=%s agent_api_key=%s panel_api_key=%s", demo_info.get("id"), demo_info.get("agent_api_key"), demo_info.get("client_panel_api_key"))

    logger.info("Init DB completado")
    return 0


if __name__ == "__main__":
    sys.exit(main())
