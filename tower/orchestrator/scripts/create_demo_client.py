import logging
import uuid

from sqlalchemy.exc import OperationalError

from app.db.session import SessionLocal
from app.models.domain import Client

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("create_demo_client")


def _generate(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex}"


def upsert_demo_client() -> Client:
    session = SessionLocal()
    try:
        client = session.query(Client).filter(Client.name == "Demo Client").first()
        if not client:
            client = Client(
                name="Demo Client",
                status="active",
                agent_api_key=_generate("client"),
                client_panel_api_key=_generate("panel"),
            )
            session.add(client)
            session.commit()
            session.refresh(client)
            logger.info("Cliente demo creado")
        else:
            updated = False
            if not client.agent_api_key:
                client.agent_api_key = _generate("client")
                updated = True
            if not client.client_panel_api_key:
                client.client_panel_api_key = _generate("panel")
                updated = True
            if updated:
                session.commit()
                session.refresh(client)
                logger.info("Cliente demo actualizado con nuevas llaves")
        return client
    finally:
        session.close()


def main():
    try:
        client = upsert_demo_client()
    except OperationalError as exc:
        logger.error("No se pudo conectar a la base de datos: %s", exc)
        return 1
    except Exception as exc:  # pragma: no cover
        logger.exception("Fallo inesperado: %s", exc)
        return 1

    print("Demo Client listo:")
    print(f"id={client.id}")
    print(f"X-Client-API-Key={client.agent_api_key}")
    print(f"Panel-API-Key={client.client_panel_api_key}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
