"""
Ejemplo sencillo de consumo de la API FastAPI.

Requiere que tengas levantado:

    uvicorn api.main:app --reload
"""

import time
from typing import Any

import requests

BASE_URL = "http://localhost:8000"


def get_municipios() -> list[str]:
    resp = requests.get(f"{BASE_URL}/municipios", timeout=30)
    resp.raise_for_status()
    data = resp.json()
    return data.get("municipios", [])


def create_job(municipios: list[str]) -> str:
    body: dict[str, Any] = {
        "municipios": municipios,
        "fecha_inicio": "2024-01-01",
        "fecha_fin": "2024-01-03",
        "chunks": 2,
    }
    resp = requests.post(f"{BASE_URL}/jobs", json=body, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    return data["job_id"]


def wait_for_completion(job_id: str) -> None:
    while True:
        resp = requests.get(f"{BASE_URL}/jobs/{job_id}", timeout=30)
        resp.raise_for_status()
        data = resp.json()
        status = data["status"]
        progress = data.get("progress")
        print(f"Estado: {status} - Progreso: {progress}")

        if status in {"completed", "failed"}:
            break

        time.sleep(2)


def get_results(job_id: str) -> None:
    resp = requests.get(f"{BASE_URL}/jobs/{job_id}/results", timeout=60)
    if resp.status_code == 409:
        print("Job aún no está listo para resultados.")
        print(resp.json())
        return
    resp.raise_for_status()
    data = resp.json()
    print(f"Resultados para job {job_id}:")
    print(f"Total registros: {len(data.get('results', []))}")
    if data.get("results"):
        print("Primeros registros:")
        for row in data["results"][:5]:
            print(row)


def main() -> None:
    municipios = get_municipios()
    if not municipios:
        print("No hay municipios disponibles desde la API.")
        return

    municipio = municipios[0]
    print(f"Usando municipio: {municipio}")

    job_id = create_job([municipio])
    print(f"Job creado: {job_id}")

    wait_for_completion(job_id)
    get_results(job_id)


if __name__ == "__main__":
    main()

