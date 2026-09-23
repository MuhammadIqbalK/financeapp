import os
import sys

os.environ["DATABASE_URL"] = "sqlite:////tmp/opencode/financeapp_test.db"
os.environ["SECRET_KEY"] = "test-secret-key-not-used-in-production"
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from fastapi.testclient import TestClient

if os.path.exists("/tmp/opencode/financeapp_test.db"):
    os.remove("/tmp/opencode/financeapp_test.db")

from app.database import Base, engine
from app.main import app

Base.metadata.create_all(engine)


@pytest.fixture(autouse=True)
def _reset_db():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield


@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture()
def auth_client(client):
    client.post(
        "/api/auth/register",
        json={"email": "tester@example.com", "password": "secret123"},
    )
    resp = client.post(
        "/api/auth/login", json={"email": "tester@example.com", "password": "secret123"}
    )
    token = resp.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client
