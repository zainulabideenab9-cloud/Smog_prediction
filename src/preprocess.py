"""Preprocessing helpers for hourly LahoreSmog data."""

from __future__ import annotations

import math

import pandas as pd

NUMERIC_COLUMNS = [
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
]


def clean_hourly(df: pd.DataFrame) -> pd.DataFrame:
    """Clean merged hourly data without shuffling time order.

    Steps:
    1. Parse timestamps and sort by time.
    2. Remove duplicate timestamps, keeping the last record.
    3. Reindex to a continuous hourly timeline so gaps are explicit.
    4. Convert measurement columns to numeric values.
    5. Interpolate short gaps in time order, then forward/back fill edges.
    """
    out = df.copy()
    out["timestamp"] = pd.to_datetime(out["timestamp"])
    out = out.sort_values("timestamp").drop_duplicates("timestamp", keep="last")

    full_index = pd.date_range(out["timestamp"].min(), out["timestamp"].max(), freq="h")
    out = out.set_index("timestamp").reindex(full_index).rename_axis("timestamp").reset_index()

    for column in NUMERIC_COLUMNS:
        if column in out:
            out[column] = pd.to_numeric(out[column], errors="coerce")

    present = [column for column in NUMERIC_COLUMNS if column in out]
    out[present] = out[present].interpolate(method="linear", limit_direction="both")
    out[present] = out[present].ffill().bfill()
    return out


def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add calendar and cyclic time features."""
    out = df.copy()
    out["hour"] = out["timestamp"].dt.hour
    out["day_of_week"] = out["timestamp"].dt.dayofweek
    out["month"] = out["timestamp"].dt.month
    out["is_weekend"] = (out["day_of_week"] >= 5).astype(int)
    out["hour_sin"] = (2 * math.pi * out["hour"] / 24).apply(math.sin)
    out["hour_cos"] = (2 * math.pi * out["hour"] / 24).apply(math.cos)
    return out
