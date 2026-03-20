"""
Ejemplo de uso del endpoint /matriz para obtener matrices de radianza.

Requiere la API levantada:
    uvicorn api.main:app --reload

Y opcionalmente NASA_API_TOKEN en .env para descargar imágenes.
"""

import time
import requests

BASE_URL = "http://localhost:8000"


def main() -> None:
    # Obtener municipios disponibles
    resp = requests.get(f"{BASE_URL}/municipios", timeout=30)
    resp.raise_for_status()
    municipios = resp.json().get("municipios", [])
    if not municipios:
        print("No hay municipios disponibles.")
        return

    municipio = municipios[0]
    print(f"Municipio: {municipio}")
    print("Creando job de matriz para 2024-01-15...")

    # Crear job
    resp = requests.post(
        f"{BASE_URL}/matriz",
        json={"municipio": municipio, "fecha": "2024-01-15"},
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    job_id = data["job_id"]
    print(f"Job creado: {job_id}")

    # Esperar completado
    while True:
        resp = requests.get(f"{BASE_URL}/matriz/{job_id}", timeout=30)
        resp.raise_for_status()
        data = resp.json()
        status = data["status"]
        progress = data.get("progress", "")
        print(f"  Estado: {status} - {progress}")

        if status in ("completed", "failed"):
            break
        time.sleep(2)

    if status == "failed":
        print(f"Error: {data.get('error', 'Desconocido')}")
        return

    # Obtener resultado
    resp = requests.get(f"{BASE_URL}/matriz/{job_id}/resultado", timeout=60)
    if resp.status_code == 409:
        print(resp.json())
        return
    resp.raise_for_status()
    result = resp.json()

    print("\n--- Resultado ---")
    print(f"Municipio: {result['municipio']}")
    print(f"Fecha: {result['fecha']}")
    print(f"Bbox: {result['bbox']}")
    print(f"Filas: {result['rows']}, Columnas: {result['cols']}")
    print(f"Radiance matrix: {len(result['radiance_matrix'])}x{len(result['radiance_matrix'][0]) if result['radiance_matrix'] else 0}")
    print(f"Municipality mask: {len(result['municipality_mask'])}x{len(result['municipality_mask'][0]) if result['municipality_mask'] else 0}")
    ones = sum(sum(row) for row in result["municipality_mask"])
    print(f"Píxeles de municipio (1s): {ones}")
    print("\nPrimeras filas de radiance_matrix:")
    for i, row in enumerate(result["radiance_matrix"][:3]):
        print(f"  [{i}]: {row[:5]}...")
    print("\nPrimeras filas de municipality_mask:")
    for i, row in enumerate(result["municipality_mask"][:3]):
        print(f"  [{i}]: {row[:5]}...")


if __name__ == "__main__":
    main()
