"""FastAPI backend and web app for LahoreSmog.

Run locally with:
    uvicorn src.api:app --reload

Then open http://127.0.0.1:8000 for the web app.
"""

from __future__ import annotations

import asyncio
from pathlib import Path

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from config import PROJECT_ROOT, SOCKET_PUSH_INTERVAL_SECONDS
from src.prediction_service import current_payload, forecast_payload, socket_payload, stations_payload

STATIC_DIR = PROJECT_ROOT / "static"

app = FastAPI(title="LahoreSmog API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def web_app() -> FileResponse:
    """Serve the LahoreSmog web app shell."""
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
def health() -> dict:
    """Return backend health for local checks and deployment probes."""
    return {"status": "ok", "service": "LahoreSmog API"}


@app.get("/current")
def current() -> dict:
    """Return latest PM2.5 and AQI."""
    return current_payload()


@app.get("/forecast")
def forecast(hours: int = 24) -> dict:
    """Return PM2.5/AQI forecasts for supported horizons."""
    return forecast_payload(hours=hours)


@app.get("/stations")
def stations() -> dict:
    """Return Lahore zones used by the dashboard map."""
    return stations_payload()


@app.websocket("/ws/predictions")
async def predictions_socket(websocket: WebSocket) -> None:
    """Push a fresh prediction payload every configured interval."""
    await websocket.accept()
    while True:
        await websocket.send_json(socket_payload())
        await asyncio.sleep(SOCKET_PUSH_INTERVAL_SECONDS)
