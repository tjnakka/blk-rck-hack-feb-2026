"""
BlackRock Retirement Savings API — Application entry point.

This module creates the FastAPI application, registers middleware,
mounts versioned API routers, and serves the React frontend.

Run with: uvicorn src.main:app --host 0.0.0.0 --port 5477
"""

import os
import time

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.config import PORT, HOST, ENV
from backend.core.logging import get_logger
from backend.api.v1.router import router as v1_router

logger = get_logger(__name__)

app = FastAPI(
    title="BlackRock Retirement Savings API",
    description="Automated retirement savings through expense-based micro-investments",
    version="1.0.0",
)


# ---------- Middleware: Request logging ----------
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration = time.perf_counter() - start
    # Only log API requests, not static file requests
    if request.url.path.startswith("/blackrock"):
        logger.info(
            f"{request.method} {request.url.path} → {response.status_code} [{duration:.3f}s]"
        )
    return response


# ---------- API Routes ----------
app.include_router(v1_router, prefix="/blackrock/challenge/v1")


# ---------- Frontend (React SPA) ----------
FRONTEND_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "frontend", "dist"
)

if os.path.isdir(FRONTEND_DIR):
    # Serve static assets (JS, CSS, images)
    static_dir = os.path.join(FRONTEND_DIR, "assets")
    if os.path.isdir(static_dir):
        app.mount("/assets", StaticFiles(directory=static_dir), name="assets")

    @app.get("/", include_in_schema=False)
    async def serve_index():
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

    @app.get("/{path:path}", include_in_schema=False)
    async def serve_spa(path: str):
        """Catch-all: serve index.html for SPA client-side routing."""
        file_path = os.path.join(FRONTEND_DIR, path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.main:app", host=HOST, port=PORT, reload=(ENV == "dev"))
