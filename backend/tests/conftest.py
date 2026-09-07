import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_session
from app.main import app

TEST_DB_URL = "sqlite:////tmp/tolti-test.db"
test_engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)
    if os.path.exists("test.db"):
        os.remove("test.db")


@pytest.fixture
def client():
    def override_get_session():
        db = TestSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def create_session(client: TestClient, display_name: str = "Tester") -> dict:
    r = client.post("/api/v1/sessions", json={"display_name": display_name})
    assert r.status_code == 201, r.text
    data = r.json()
    assert "session_token" in data
    return data


def auth_headers(client: TestClient, session_token: str) -> dict:
    return {"Cookie": f"tolti_session={session_token}"}


def create_room(client: TestClient, session_token: str, name: str = "Test room") -> dict:
    r = client.post(
        "/api/v1/rooms",
        json={"name": name},
        headers=auth_headers(client, session_token),
    )
    assert r.status_code == 201, r.text
    return r.json()
