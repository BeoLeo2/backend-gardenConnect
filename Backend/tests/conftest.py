"""Configuration des tests"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel
from shared.database import get_db

@pytest.fixture
def client():
    from services.auth_service.main import app
    return TestClient(app)

@pytest.fixture
def test_db():
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
