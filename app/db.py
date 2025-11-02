from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from .settings import settings

# Creates SQLAlchemy engine for SQLite
engine = create_engine(
    settings.db_url,
    connect_args={"check_same_thread": False}
    if settings.db_url.startswith("sqlite")
    else {},
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()