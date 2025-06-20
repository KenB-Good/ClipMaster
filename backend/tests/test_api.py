import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.endpoints.system import router as system_router

app = FastAPI()
app.include_router(system_router, prefix="/api/v1/system")

@pytest.fixture
def client(monkeypatch):
    with TestClient(app) as client:
        yield client


def test_system_health_endpoint(client, monkeypatch):
    async def fake_health(self):
        return {"disk_usage": 10, "memory_usage": 20, "recommendations": [], "directory_usage": {}}
    monkeypatch.setattr("app.services.system_service.SystemService.check_storage_usage", fake_health)
    response = client.get("/api/v1/system/health")
    assert response.status_code == 200
    assert response.json()["disk_usage"] == 10
