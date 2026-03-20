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
            {
                "Fecha": "2024-01-01",
                "Municipio": "iztapalapa",
                "Cantidad_de_pixeles": 100,
                "Suma_de_radianza": 1000.0,
                "Media_de_radianza": 10.0,
                "Desviacion_estandar_de_radianza": 1.0,
                "Maximo_de_radianza": 12.0,
                "Minimo_de_radianza": 8.0,
                "Percentil_25_de_radianza": 9.0,
                "Percentil_50_de_radianza": 10.0,
                "Percentil_75_de_radianza": 11.0,
            },
        ]
        resp = client.get("/jobs/done-job/results")
        assert resp.status_code == 200
        data = resp.json()
        assert data["job_id"] == "done-job"
        assert len(data["results"]) == 1
        assert data["results"][0]["Municipio"] == "iztapalapa"
        assert data["results"][0]["Media_de_radianza"] == 10.0


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


# --- POST /matriz ---


class TestPostMatriz:
    def test_returns_202_and_job_id_when_valid(self, client):
        with patch("api.routes._get_available_municipios", return_value=["iztapalapa"]):
            with patch("api.routes.run_matriz_job", new_callable=AsyncMock):
                resp = client.post(
                    "/matriz",
                    json={"municipio": "Iztapalapa", "fecha": "2024-01-15"},
                )
        assert resp.status_code == 202
        data = resp.json()
        assert "job_id" in data
        assert data["status"] == "pending"

    def test_returns_400_when_municipio_invalid(self, client):
        with patch("api.routes._get_available_municipios", return_value=["iztapalapa"]):
            resp = client.post(
                "/matriz",
                json={"municipio": "unknown", "fecha": "2024-01-15"},
            )
        assert resp.status_code == 400
        assert "not available" in resp.json().get("detail", "")


# --- GET /matriz/{job_id} ---


class TestGetMatrizStatus:
    def test_returns_404_when_job_unknown(self, client):
        resp = client.get("/matriz/00000000-0000-0000-0000-000000000000")
        assert resp.status_code == 404

    def test_returns_200_with_status_when_job_exists(self, client):
        state = job_store.create("matriz-job-123")
        state.status = "completed"
        state.total_results = 1
        resp = client.get("/matriz/matriz-job-123")
        assert resp.status_code == 200
        assert resp.json()["job_id"] == "matriz-job-123"
        assert resp.json()["status"] == "completed"


# --- GET /matriz/{job_id}/resultado ---


class TestGetMatrizResult:
    def test_returns_404_when_job_unknown(self, client):
        resp = client.get("/matriz/00000000-0000-0000-0000-000000000000/resultado")
        assert resp.status_code == 404

    def test_returns_409_when_job_not_finished(self, client):
        state = job_store.create("matriz-running")
        state.status = "running"
        resp = client.get("/matriz/matriz-running/resultado")
        assert resp.status_code == 409
        assert "not finished" in resp.json().get("detail", "").lower()

    def test_returns_200_with_matrices_when_completed(self, client):
        state = job_store.create("matriz-done")
        state.status = "completed"
        state.results = [
            {
                "job_id": "matriz-done",
                "municipio": "iztapalapa",
                "fecha": "2024-01-15",
                "bbox": {"min_x": 0, "max_x": 10, "min_y": 0, "max_y": 10},
                "rows": 11,
                "cols": 11,
                "radiance_matrix": [[0.1] * 11 for _ in range(11)],
                "municipality_mask": [[1 if i == j else 0 for j in range(11)] for i in range(11)],
            }
        ]
        resp = client.get("/matriz/matriz-done/resultado")
        assert resp.status_code == 200
        data = resp.json()
        assert data["job_id"] == "matriz-done"
        assert data["municipio"] == "iztapalapa"
        assert data["fecha"] == "2024-01-15"
        assert data["rows"] == 11
        assert data["cols"] == 11
        assert len(data["radiance_matrix"]) == 11
        assert len(data["municipality_mask"]) == 11
