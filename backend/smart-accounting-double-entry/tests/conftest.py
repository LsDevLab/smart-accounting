import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from infrastructure.database import Base, get_db
import models


import os

# Use a temporary file-based SQLite database for tests to support multiple threads/connections
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_temp.db"

# Cleanup any existing test DB file
if os.path.exists("./test_temp.db"):
    try:
        os.remove("./test_temp.db")
    except Exception:
        pass


engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(name="db", scope="function")
def db_fixture():
    # Recreate all tables for a clean slate
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="session", autouse=True)
def cleanup_temp_db():
    yield
    if os.path.exists("./test_temp.db"):
        try:
            os.remove("./test_temp.db")
        except Exception:
            pass


@pytest.fixture(name="client", scope="function")
def client_fixture(db):
    # Override get_db dependency in the FastAPI application
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
