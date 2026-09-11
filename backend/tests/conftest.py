import os
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
# Ensure tables exist before any test
from app.db import init_db, Base, engine
import pytest

@pytest.fixture(scope="session", autouse=True)
def setup_db():
    # Drop and create for clean state
    Base.metadata.drop_all(bind=engine)
    init_db()
    yield
    # cleanup
    try:
        os.remove("test.db")
    except FileNotFoundError:
        pass
    try:
        os.remove("backend/test.db")
    except FileNotFoundError:
        pass
