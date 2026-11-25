"""Dashboard data helpers kept separate from Streamlit rendering."""

from __future__ import annotations

import pandas as pd

from src.prediction_service import current_payload, forecast_payload, stations_payload


def aqi_color(aqi: int) -> str:
    """Return a display colour for an AQI value."""
    if aqi <= 50:
        return "green"
    if aqi <= 100:
        return "yellow"
    if aqi <= 150:
        return "orange"
    if aqi <= 200:
        return "red"
    if aqi <= 300:
        return "purple"
    return "maroon"


def dashboard_frames() -> tuple[dict, pd.DataFrame, pd.DataFrame]:
    """Return current payload, forecast frame, and station frame."""
    current = current_payload()
    forecast = pd.DataFrame(forecast_payload(24)["forecast"])
    stations = pd.DataFrame(stations_payload()["stations"])
    if not stations.empty:
        stations["aqi"] = current["aqi"]
        stations["color"] = stations["aqi"].apply(aqi_color)
    return current, forecast, stations
