"""FastAPI application entry point for VNP46A1 Satellite API."""
from fastapi import FastAPI

from api.routes import router

app = FastAPI(
    title="VNP46A1 Satellite API",
    version="1.0.0",
    description="Async API for satellite image processing (VNP46A1) with background jobs.",
)
app.include_router(router)
