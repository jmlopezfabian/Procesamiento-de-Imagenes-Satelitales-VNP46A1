"""FastAPI routes for VNP46A1 satellite processing API."""
import asyncio
import json
import uuid
from datetime import timedelta

from fastapi import APIRouter, HTTPException

from satellite_async.config import PIXELES_MUNICIPIOS
from satellite_async.models import MedicionResultado

from .job_manager import job_store, run_job
from .schemas import JobRequest, JobResult, JobStatus, MunicipiosResponse

router = APIRouter()


def _get_available_municipios() -> list[str]:
    """Load municipality names from config JSON path."""
    with open(PIXELES_MUNICIPIOS, "r", encoding="utf-8") as f:
        data = json.load(f)
    return list(data.keys())


def _build_fechas(fecha_inicio, fecha_fin) -> list[str]:
    """Build list of date strings dd-mm-yy from inicio to fin (inclusive)."""
    fechas = []
    d = fecha_inicio
    while d <= fecha_fin:
        fechas.append(d.strftime("%d-%m-%y"))
        d += timedelta(days=1)
    return fechas


@router.get("/municipios", response_model=MunicipiosResponse)
async def list_municipios():
    """List available municipality names for processing."""
    municipios = _get_available_municipios()
    return MunicipiosResponse(municipios=municipios)


@router.post("/jobs", response_model=JobStatus, status_code=202)
async def create_job(body: JobRequest):
    """Create a new processing job. Returns immediately with job_id; poll GET /jobs/{job_id} for status."""
    available = _get_available_municipios()
    normalized = [m.lower().strip() for m in body.municipios]
    invalid = [m for m in normalized if m not in available]
    if invalid:
        raise HTTPException(
            status_code=400,
            detail=f"Municipios not available: {invalid}. Use GET /municipios for the list.",
        )
    if body.fecha_fin < body.fecha_inicio:
        raise HTTPException(status_code=400, detail="fecha_fin must be >= fecha_inicio")

    fechas = _build_fechas(body.fecha_inicio, body.fecha_fin)
    if not fechas:
        raise HTTPException(status_code=400, detail="No dates in range")

    job_id = str(uuid.uuid4())
    state = job_store.create(job_id)
    task = asyncio.create_task(
        run_job(job_id, normalized, fechas, body.chunks)
    )
    job_store.set_task(job_id, task)

    return JobStatus(
        job_id=job_id,
        status=state.status,
        progress=state.progress,
        created_at=state.created_at,
        finished_at=state.finished_at,
        error=state.error,
        total_results=state.total_results,
    )


@router.get("/jobs/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: str):
    """Get current status and progress of a job."""
    state = job_store.get(job_id)
    if not state:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobStatus(
        job_id=state.job_id,
        status=state.status,
        progress=state.progress,
        created_at=state.created_at,
        finished_at=state.finished_at,
        error=state.error,
        total_results=state.total_results,
    )


@router.get("/jobs/{job_id}/results", response_model=JobResult)
async def get_job_results(job_id: str):
    """Get results of a completed job. Returns 409 if job is not yet completed."""
    state = job_store.get(job_id)
    if not state:
        raise HTTPException(status_code=404, detail="Job not found")
    if state.status not in ("completed", "failed"):
        raise HTTPException(
            status_code=409,
            detail=f"Job not finished (status: {state.status}). Poll GET /jobs/{job_id}.",
        )
    if state.status == "failed":
        raise HTTPException(
            status_code=409,
            detail=f"Job failed: {state.error or 'Unknown error'}",
        )
    results = [MedicionResultado.model_validate(r) for r in state.results]
    return JobResult(job_id=job_id, results=results)


@router.delete("/jobs/{job_id}", status_code=204)
async def cancel_job(job_id: str):
    """Cancel a pending or running job and remove it from the store."""
    state = job_store.get(job_id)
    if not state:
        raise HTTPException(status_code=404, detail="Job not found")
    if state.task and not state.task.done():
        state.task.cancel()
        try:
            await state.task
        except asyncio.CancelledError:
            pass
    job_store.remove(job_id)
