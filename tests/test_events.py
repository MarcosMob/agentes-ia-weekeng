from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app import database
from app.main import app


@pytest.fixture()
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    """Cria um TestClient isolado apontando para um banco SQLite temporário."""
    temp_db = tmp_path / "test_events.db"
    monkeypatch.setattr(database, "DB_PATH", temp_db)
    with TestClient(app) as test_client:
        yield test_client


def test_list_events_returns_seeded_events(client: TestClient) -> None:
    """GET /api/events deve retornar HTTP 200 e os 2 eventos iniciais de seed."""
    response = client.get("/api/events")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert {"id", "title", "speaker", "capacity", "created_at"} <= set(data[0].keys())


def test_create_event_returns_201_and_persists(client: TestClient) -> None:
    """POST /api/events deve retornar HTTP 201 e persistir o evento no banco."""
    payload = {
        "title": "Oficina de Testes Automatizados",
        "speaker": "João Pedro Souza",
        "capacity": 25,
    }
    response = client.post("/api/events", json=payload)
    assert response.status_code == 201

    created = response.json()
    assert created["title"] == payload["title"]
    assert created["speaker"] == payload["speaker"]
    assert created["capacity"] == payload["capacity"]
    assert isinstance(created["id"], int)

    list_response = client.get("/api/events")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 3
