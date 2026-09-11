from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import settings
import os

def _database_url():
    # Use sqlite for tests / when postgres not reachable or env override
    if os.getenv("PYTEST_CURRENT_TEST") or os.getenv("DATABASE_URL", "").startswith("sqlite"):
        return os.getenv("DATABASE_URL", "sqlite:///./test.db")
    # Allow explicit override via DATABASE_URL env
    env_url = os.getenv("DATABASE_URL")
    if env_url:
        return env_url
    return settings.database_url

def _get_engine():
    url = _database_url()
    # sqlite needs check_same_thread=False
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    return create_engine(url, pool_pre_ping=True, future=True, connect_args=connect_args)

engine = _get_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    from . import models  # noqa
    Base.metadata.create_all(bind=engine)
