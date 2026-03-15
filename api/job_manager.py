"""In-memory job store and background job execution for satellite processing."""
import asyncio
from datetime import datetime
from typing import Literal

from satellite_async.satellite_async import SatelliteImagesAsync


class JobState:
    """Mutable state for a single job."""

    def __init__(self, job_id: str):
        self.job_id = job_id
        self.status: Literal["pending", "running", "completed", "failed"] = "pending"
        self.progress: str | None = None
        self.created_at = datetime.utcnow()
        self.finished_at: datetime | None = None
        self.error: str | None = None
        self.results: list[dict] = []
        self.total_results: int = 0
        self.task: asyncio.Task | None = None


class JobStore:
    """In-memory store for job states. Single instance used by the API."""

    def __init__(self):
        self._jobs: dict[str, JobState] = {}

    def create(self, job_id: str) -> JobState:
        state = JobState(job_id)
        self._jobs[job_id] = state
        return state

    def get(self, job_id: str) -> JobState | None:
        return self._jobs.get(job_id)

    def set_task(self, job_id: str, task: asyncio.Task) -> None:
        state = self._jobs.get(job_id)
        if state:
            state.task = task

    def remove(self, job_id: str) -> None:
        self._jobs.pop(job_id, None)


job_store = JobStore()


async def run_job(
    job_id: str,
    municipios: list[str],
    fechas: list[str],
    chunks: int | None,
) -> None:
    """
    Run satellite processing in the background. Updates the job state in job_store.
    """
    state = job_store.get(job_id)
    if not state:
        return
    state.status = "running"
    state.progress = "0/" + str(len(fechas)) + " fechas"

    def on_progress(progress: str) -> None:
        if state:
            state.progress = progress

    try:
        sat = SatelliteImagesAsync(municipios)
        df = await sat.run(
            fechas,
            chunks=chunks,
            save_progress_enabled=False,
            on_progress=on_progress,
        )
        state.results = df.to_dict(orient="records") if not df.empty else []
        state.status = "completed"
        state.total_results = len(state.results)
    except asyncio.CancelledError:
        state.status = "failed"
        state.error = "Job cancelled"
    except Exception as e:
        state.status = "failed"
        state.error = str(e)
    finally:
        state.finished_at = datetime.utcnow()
