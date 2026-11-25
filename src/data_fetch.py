"""Data fetching for LahoreSmog.

Chunk 1 uses Open-Meteo because it is free and does not need an API key. The
air-quality values are modelled/gridded estimates, not official station
observations, so the README and viva notes should describe them honestly.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import requests

from config import LAHORE_LATITUDE, LAHORE_LONGITUDE, RAW_DATA_DIR

AIR_QUALITY_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

AIR_QUALITY_VARIABLES = [
    "pm2_5",
    "pm10",
    "carbon_monoxide",
    "nitrogen_dioxide",
    "sulphur_dioxide",
    "ozone",
]

WEATHER_VARIABLES = [
    "temperature_2m",
    "relative_humidity_2m",
    "wind_speed_10m",
    "wind_direction_10m",
    "precipitation",
    "surface_pressure",
]


def _hourly_to_frame(payload: dict, variables: list[str]) -> pd.DataFrame:
    """Convert an Open-Meteo hourly payload into a tidy DataFrame."""
    hourly = payload.get("hourly", {})
    if "time" not in hourly:
        raise ValueError("Open-Meteo payload does not contain hourly.time")

    frame = pd.DataFrame({"timestamp": pd.to_datetime(hourly["time"])})
    for variable in variables:
        frame[variable] = hourly.get(variable)
    return frame


def fetch_open_meteo_air_quality(
    latitude: float = LAHORE_LATITUDE,
    longitude: float = LAHORE_LONGITUDE,
    past_days: int = 14,
    forecast_days: int = 1,
    session: requests.Session | None = None,
) -> pd.DataFrame:
    """Fetch hourly PM2.5 and related pollutants for Lahore."""
    client = session or requests.Session()
    response = client.get(
        AIR_QUALITY_URL,
        params={
            "latitude": latitude,
            "longitude": longitude,
            "hourly": ",".join(AIR_QUALITY_VARIABLES),
            "timezone": "Asia/Karachi",
            "past_days": past_days,
            "forecast_days": forecast_days,
        },
        timeout=30,
    )
    response.raise_for_status()
    return _hourly_to_frame(response.json(), AIR_QUALITY_VARIABLES)


def fetch_open_meteo_weather(
    latitude: float = LAHORE_LATITUDE,
    longitude: float = LAHORE_LONGITUDE,
    past_days: int = 14,
    forecast_days: int = 1,
    session: requests.Session | None = None,
) -> pd.DataFrame:
    """Fetch hourly weather variables that affect smog dispersion."""
    client = session or requests.Session()
    response = client.get(
        WEATHER_URL,
        params={
            "latitude": latitude,
            "longitude": longitude,
            "hourly": ",".join(WEATHER_VARIABLES),
            "timezone": "Asia/Karachi",
            "past_days": past_days,
            "forecast_days": forecast_days,
        },
        timeout=30,
    )
    response.raise_for_status()
    return _hourly_to_frame(response.json(), WEATHER_VARIABLES)


def merge_hourly(air_quality: pd.DataFrame, weather: pd.DataFrame) -> pd.DataFrame:
    """Merge air-quality and weather frames on timestamp."""
    merged = pd.merge(air_quality, weather, on="timestamp", how="inner")
    return merged.sort_values("timestamp").reset_index(drop=True)


def coverage_report(df: pd.DataFrame) -> dict:
    """Summarise completeness so weak data coverage is visible early."""
    if df.empty:
        return {"rows": 0, "start": None, "end": None, "missing_pct": {}}

    missing_pct = {
        column: round(float(df[column].isna().mean() * 100), 2)
        for column in df.columns
        if column != "timestamp"
    }
    return {
        "rows": int(len(df)),
        "start": str(df["timestamp"].min()),
        "end": str(df["timestamp"].max()),
        "missing_pct": missing_pct,
        "pm25_non_null": int(df["pm2_5"].notna().sum()) if "pm2_5" in df else 0,
    }


def fetch_lahore_dataset(past_days: int = 14, forecast_days: int = 1) -> pd.DataFrame:
    """Fetch and merge the Lahore hourly dataset."""
    air_quality = fetch_open_meteo_air_quality(past_days=past_days, forecast_days=forecast_days)
    weather = fetch_open_meteo_weather(past_days=past_days, forecast_days=forecast_days)
    return merge_hourly(air_quality, weather)


def save_dataset(df: pd.DataFrame, output_path: Path | None = None) -> Path:
    """Save the merged dataset as CSV under data/raw by default."""
    path = output_path or (RAW_DATA_DIR / "lahore_hourly.csv")
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch Lahore hourly air-quality and weather data")
    parser.add_argument("--past-days", type=int, default=14)
    parser.add_argument("--forecast-days", type=int, default=1)
    args = parser.parse_args()

    df = fetch_lahore_dataset(past_days=args.past_days, forecast_days=args.forecast_days)
    path = save_dataset(df)
    report = coverage_report(df)

    print(f"Saved {report['rows']} rows to {path}")
    print(f"Coverage: {report['start']} to {report['end']}")
    print(f"PM2.5 non-null rows: {report['pm25_non_null']}")
    print("Missing % by column:")
    for column, pct in report["missing_pct"].items():
        print(f"- {column}: {pct}%")


if __name__ == "__main__":
    main()
