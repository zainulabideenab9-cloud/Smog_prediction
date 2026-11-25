"""Smoke test for the LahoreSmog backend.

Run after installing requirements:
    python scripts/smoke_test.py

This checks route registration and core payload shapes without starting a
server or depending on live data files.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.api import app, health
from src.prediction_service import current_payload, forecast_payload, stations_payload


def main() -> None:
    paths = {route.path for route in app.routes}
    required = {"/", "/health", "/current", "/forecast", "/stations", "/ws/predictions"}
    missing = required - paths
    if missing:
        raise SystemExit(f"Missing routes: {sorted(missing)}")

    if health()["status"] != "ok":
        raise SystemExit("Health check failed")

    frame = pd.DataFrame({"timestamp": pd.to_datetime(["2026-11-25 10:00"]), "pm2_5": [160.0]})
    current = current_payload(frame)
    forecast = forecast_payload(24, frame=frame, models={})
    stations = stations_payload()

    assert current["aqi"] > 200
    assert len(forecast["forecast"]) == 4
    assert stations["stations"]
    print("Smoke test passed: routes, health, current, forecast, and stations are OK")


if __name__ == "__main__":
    main()
