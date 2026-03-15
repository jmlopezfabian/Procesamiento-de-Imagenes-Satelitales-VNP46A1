"""Pydantic schemas for API request/response."""
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field

from satellite_async.models import MedicionResultado


class JobRequest(BaseModel):
    """Body for POST /jobs."""

    municipios: list[str] = Field(..., min_length=1, description="List of municipality names")
    fecha_inicio: date = Field(..., description="Start date (inclusive)")
    fecha_fin: date = Field(..., description="End date (inclusive)")
    chunks: int | None = Field(None, description="Optional chunk size for processing dates in batches")


class JobStatus(BaseModel):
    """Response for job status (GET /jobs/{job_id})."""

    job_id: str
    status: Literal["pending", "running", "completed", "failed"] = Field(
        ..., description="Current job status"
    )
    progress: str | None = Field(None, description="Human-readable progress e.g. '3/10 fechas'")
    created_at: datetime = Field(..., description="When the job was created")
    finished_at: datetime | None = Field(None, description="When the job finished (if completed/failed)")
    error: str | None = Field(None, description="Error message if status is failed")
    total_results: int = Field(0, description="Number of measurement records when completed")


class JobResult(BaseModel):
    """Response for GET /jobs/{job_id}/results."""

    job_id: str
    results: list[MedicionResultado] = Field(
        ..., description="List of measurement records (MedicionResultado)"
    )


class MunicipiosResponse(BaseModel):
    """Response for GET /municipios."""

    municipios: list[str] = Field(..., description="Available municipality names")
