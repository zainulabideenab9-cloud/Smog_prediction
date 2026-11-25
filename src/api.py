"""FastAPI service for LahoreSmog.

Run locally with:
    uvicorn src.api:app --reload
"""

from __future__ import annotations

import asyncio

from fastapi import FastAPI, WebSocket

from config import SOCKET_PUSH_INTERVAL_SECONDS
from src.prediction_service import current_payload, forecast_payload, socket_payload, stations_payload

app = FastAPI(title="LahoreSmog API")


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
