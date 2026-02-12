from app.db.session import engine
from app.models.domain import Base

def init_tables():
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created.")

if __name__ == "__main__":
    init_tables()
