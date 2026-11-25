"""Feature engineering for multi-horizon PM2.5 forecasting."""

from __future__ import annotations

import pandas as pd

from config import FORECAST_HORIZONS_HOURS
from src.preprocess import add_time_features, clean_hourly

BASE_FEATURES = [
    "pm2_5",
    "pm10",
    "carbon_monoxide",
    "nitrogen_dioxide",
    "sulphur_dioxide",
    "ozone",
    "temperature_2m",
    "relative_humidity_2m",
    "wind_speed_10m",
    "wind_direction_10m",
    "precipitation",
    "surface_pressure",
    "hour",
    "day_of_week",
    "month",
    "is_weekend",
    "hour_sin",
    "hour_cos",
]


def add_lag_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add PM2.5 lag and rolling-window features.

    Lags use only past values. Rolling features are shifted by one hour before
    aggregation so the current row never leaks its own target into training.
    """
    out = df.copy()
    for lag in [1, 3, 6, 12, 24]:
        out[f"pm25_lag_{lag}h"] = out["pm2_5"].shift(lag)

    shifted = out["pm2_5"].shift(1)
    for window in [3, 6, 12, 24]:
        out[f"pm25_mean_{window}h"] = shifted.rolling(window).mean()
        out[f"pm25_max_{window}h"] = shifted.rolling(window).max()
    return out


def add_targets(df: pd.DataFrame, horizons: list[int] | None = None) -> pd.DataFrame:
    """Add future PM2.5 targets for each forecast horizon."""
    out = df.copy()
    for horizon in horizons or FORECAST_HORIZONS_HOURS:
        out[f"target_pm25_{horizon}h"] = out["pm2_5"].shift(-horizon)
    return out


def build_feature_frame(df: pd.DataFrame) -> pd.DataFrame:
    """Clean data and build model-ready features and targets."""
    cleaned = clean_hourly(df)
    featured = add_time_features(cleaned)
    featured = add_lag_features(featured)
    featured = add_targets(featured)
    return featured.dropna().reset_index(drop=True)


def feature_columns(df: pd.DataFrame) -> list[str]:
    """Return feature columns present in a built feature frame."""
    lag_columns = [column for column in df.columns if column.startswith("pm25_lag_") or column.startswith("pm25_mean_") or column.startswith("pm25_max_")]
    return [column for column in BASE_FEATURES + lag_columns if column in df.columns]
