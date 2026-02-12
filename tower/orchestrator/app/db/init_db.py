import logging

from app.db.session import engine
from app.db.base import Base

# Importamos los modelos para que se registren en el metadata
from app.models import domain  # noqa: F401


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def init_db() -> None:
    """
    Crea todas las tablas definidas en los modelos SQLAlchemy.
    Se ejecuta dentro del contenedor del orchestrator.
    """
    logger.info("Creando tablas de la base de datos Deco-Security...")
    Base.metadata.create_all(bind=engine)
    logger.info("Tablas creadas (o ya existentes).")


if __name__ == "__main__":
    init_db()
