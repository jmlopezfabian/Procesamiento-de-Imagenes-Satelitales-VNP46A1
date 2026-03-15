"""Tests for FastAPI satellite API endpoints. Use mocks to avoid NASA/processing."""
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from api.main import app
from api.job_manager import job_store

# Client fixture
@pytest.fixture
def client():
    return TestClient(app)


# Clear job_store before each test so tests don't see each other's jobs
@pytest.fixture(autouse=True)
def clear_job_store():
    for job_id in list(job_store._jobs.keys()):
        job_store.remove(job_id)
    yield
    for job_id in list(job_store._jobs.keys()):
        job_store.remove(job_id)


# --- GET /municipios ---

class TestGetMunicipios:
    def test_returns_200_and_municipios_list(self, client):
        with patch("api.routes._get_available_municipios", return_value=["iztapalapa", "tlalpan"]):
            resp = client.get("/municipios")
        assert resp.status_code == 200
        data = resp.json()
        assert "municipios" in data
        assert data["municipios"] == ["iztapalapa", "tlalpan"]


# --- POST /jobs ---

class TestPostJobs:
    def test_returns_202_and_job_id_when_valid(self, client):
        with patch("api.routes._get_available_municipios", return_value=["iztapalapa", "tlalpan"]):
            with patch("api.routes.run_job", new_callable=AsyncMock):
                resp = client.post(
                    "/jobs",
                    json={
                        "municipios": ["Iztapalapa"],
                        "fecha_inicio": "2024-01-01",
                        "fecha_fin": "2024-01-03",
                        "chunks": None,
                    },
                )
        assert resp.status_code == 202
        data = resp.json()
        assert "job_id" in data
        assert data["status"] == "pending"
        assert data["job_id"]

    def test_returns_400_when_municipios_invalid(self, client):
        with patch("api.routes._get_available_municipios", return_value=["iztapalapa"]):
            resp = client.post(
                "/jobs",
                json={
                    "municipios": ["unknown"],
                    "fecha_inicio": "2024-01-01",
                    "fecha_fin": "2024-01-03",
                },
            )
        assert resp.status_code == 400
        assert "not available" in resp.json().get("detail", "")

    def test_returns_400_when_fecha_fin_before_fecha_inicio(self, client):
        with patch("api.routes._get_available_municipios", return_value=["iztapalapa"]):
            with patch("api.routes.run_job", new_callable=AsyncMock):
                resp = client.post(
                    "/jobs",
                    json={
                        "municipios": ["iztapalapa"],
                        "fecha_inicio": "2024-01-05",
                        "fecha_fin": "2024-01-01",
                    },
                )
        assert resp.status_code == 400
        assert "fecha_fin" in resp.json().get("detail", "")


# --- GET /jobs/{job_id} ---

class TestGetJobStatus:
    def test_returns_404_when_job_unknown(self, client):
        resp = client.get("/jobs/00000000-0000-0000-0000-000000000000")
        assert resp.status_code == 404
        assert "not found" in resp.json().get("detail", "").lower()

    def test_returns_200_with_status_when_job_exists(self, client):
        state = job_store.create("test-job-123")
        state.status = "completed"
        state.total_results = 5
        resp = client.get("/jobs/test-job-123")
        assert resp.status_code == 200
        data = resp.json()
        assert data["job_id"] == "test-job-123"
        assert data["status"] == "completed"
        assert data["total_results"] == 5


# --- GET /jobs/{job_id}/results ---

class TestGetJobResults:
    def test_returns_404_when_job_unknown(self, client):
        resp = client.get("/jobs/00000000-0000-0000-0000-000000000000/results")
        assert resp.status_code == 404

    def test_returns_409_when_job_not_finished(self, client):
        state = job_store.create("running-job")
        state.status = "running"
        resp = client.get("/jobs/running-job/results")
        assert resp.status_code == 409
        assert "not finished" in resp.json().get("detail", "").lower()

    def test_returns_200_with_results_when_job_completed(self, client):
        state = job_store.create("done-job")
        state.status = "completed"
        state.results = [
            {"Fecha": "2024-01-01", "Municipio": "iztapalapa", "Media_de_radianza": 10.0},
        ]
        resp = client.get("/jobs/done-job/results")
        assert resp.status_code == 200
        data = resp.json()
        assert data["job_id"] == "done-job"
        assert data["results"] == state.results


# --- DELETE /jobs/{job_id} ---

class TestDeleteJob:
    def test_returns_404_when_job_unknown(self, client):
        resp = client.delete("/jobs/00000000-0000-0000-0000-000000000000")
        assert resp.status_code == 404

    def test_returns_204_and_removes_job(self, client):
        job_store.create("to-delete")
        assert job_store.get("to-delete") is not None
        resp = client.delete("/jobs/to-delete")
        assert resp.status_code == 204
        assert job_store.get("to-delete") is None
