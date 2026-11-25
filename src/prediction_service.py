"""Prediction payload logic shared by API, socket, and dashboard."""

from __future__ import annotations

import pickle
from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd

from config import MODEL_DIR, RAW_DATA_DIR
from src.aqi import aqi_category, pm25_to_aqi
from src.features import build_feature_frame
from src.stations import LAHORE_ZONES


def load_latest_frame() -> pd.DataFrame:
    """Load raw data and build the feature frame used for prediction."""
    path = RAW_DATA_DIR / "lahore_hourly.csv"
    if not path.exists():
        raise FileNotFoundError("Run python -m src.data_fetch first")
    raw = pd.read_csv(path, parse_dates=["timestamp"])
    return build_feature_frame(raw)


def load_models() -> dict | None:
    """Load trained models if the local pickle exists."""
    path = MODEL_DIR / "lahoresmog_models.pkl"
    if not path.exists():
        return None
    with path.open("rb") as handle:
        return pickle.load(handle)


def predict_pm25(frame: pd.DataFrame, horizon_hours: int, models: dict | None = None) -> float:
    """Predict PM2.5 for a horizon, falling back to persistence if needed."""
    latest = frame.iloc[[-1]]
    bundle = (models or {}).get(f"{horizon_hours}h")
    if not bundle:
        return float(latest["pm2_5"].iloc[0])
    prediction = bundle["model"].predict(latest[bundle["features"]])[0]
    return float(np.clip(prediction, 0, None))


def current_payload(frame: pd.DataFrame | None = None) -> dict:
    """Return the latest observed PM2.5 and AQI payload."""
    frame = frame if frame is not None else load_latest_frame()
    latest = frame.iloc[-1]
    pm25 = float(latest["pm2_5"])
    aqi = pm25_to_aqi(pm25)
    return {
        "timestamp": str(latest["timestamp"]),
        "pm25": round(pm25, 1),
        "aqi": aqi,
        "category": aqi_category(aqi),
        "source": "Open-Meteo modelled estimate",
    }


def forecast_payload(hours: int = 24, frame: pd.DataFrame | None = None, models: dict | None = None) -> dict:
    """Return forecast points for supported horizons up to the requested hours."""
    frame = frame if frame is not None else load_latest_frame()
    models = models if models is not None else load_models()
    latest_time = pd.to_datetime(frame.iloc[-1]["timestamp"])
    points = []
    for horizon in [1, 6, 12, 24]:
        if horizon > hours:
            continue
        pm25 = predict_pm25(frame, horizon, models)
        aqi = pm25_to_aqi(pm25)
        points.append(
            {
                "timestamp": str(latest_time + timedelta(hours=horizon)),
                "horizon_hours": horizon,
                "pm25": round(pm25, 1),
                "aqi": aqi,
                "category": aqi_category(aqi),
            }
        )
    return {"generated_at": datetime.now(timezone.utc).isoformat(), "forecast": points}


def stations_payload() -> dict:
    """Return Lahore zone metadata for maps and station lists."""
    return {"stations": LAHORE_ZONES}


def socket_payload() -> dict:
    """Return one live prediction payload for the WebSocket stream."""
    return {"current": current_payload(), "forecast": forecast_payload(24)["forecast"]}
