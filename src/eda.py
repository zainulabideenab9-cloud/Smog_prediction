"""Exploratory analysis and data-quality reporting."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from config import PROJECT_ROOT, RAW_DATA_DIR
from src.aqi import pm25_to_aqi
from src.data_fetch import fetch_lahore_dataset, save_dataset
from src.preprocess import clean_hourly

REPORT_PATH = PROJECT_ROOT / "reports" / "eda_summary.md"


def load_or_fetch_dataset() -> pd.DataFrame:
    """Load the raw CSV if present; otherwise fetch a short sample."""
    path = RAW_DATA_DIR / "lahore_hourly.csv"
    if path.exists():
        return pd.read_csv(path, parse_dates=["timestamp"])
    df = fetch_lahore_dataset(past_days=14, forecast_days=1)
    save_dataset(df, path)
    return df


def summarise_dataset(df: pd.DataFrame) -> dict:
    """Return the key EDA facts used in the Markdown report."""
    cleaned = clean_hourly(df)
    pm25 = cleaned["pm2_5"]
    hourly_profile = cleaned.groupby(cleaned["timestamp"].dt.hour)["pm2_5"].mean()
    correlations = cleaned.corr(numeric_only=True)["pm2_5"].drop(labels=["pm2_5"], errors="ignore")
    top_correlations = correlations.reindex(correlations.abs().sort_values(ascending=False).index).head(5)

    return {
        "rows": int(len(cleaned)),
        "start": str(cleaned["timestamp"].min()),
        "end": str(cleaned["timestamp"].max()),
        "pm25_mean": round(float(pm25.mean()), 2),
        "pm25_median": round(float(pm25.median()), 2),
        "pm25_max": round(float(pm25.max()), 2),
        "pm25_max_aqi": pm25_to_aqi(float(pm25.max())),
        "worst_hour": int(hourly_profile.idxmax()),
        "best_hour": int(hourly_profile.idxmin()),
        "top_correlations": {name: round(float(value), 3) for name, value in top_correlations.items()},
        "missing_after_cleaning": int(cleaned.isna().sum().sum()),
    }


def write_eda_report(df: pd.DataFrame, output_path: Path = REPORT_PATH) -> Path:
    """Write a plain-language EDA summary for the report and viva."""
    summary = summarise_dataset(df)
    lines = [
        "# EDA summary",
        "",
        f"- Rows after hourly cleaning: {summary['rows']}",
        f"- Time range: {summary['start']} to {summary['end']}",
        f"- PM2.5 mean: {summary['pm25_mean']} ug/m3",
        f"- PM2.5 median: {summary['pm25_median']} ug/m3",
        f"- PM2.5 maximum: {summary['pm25_max']} ug/m3 (AQI {summary['pm25_max_aqi']})",
        f"- Worst average hour: {summary['worst_hour']}:00",
        f"- Best average hour: {summary['best_hour']}:00",
        f"- Missing cells after cleaning: {summary['missing_after_cleaning']}",
        "",
        "## Strongest PM2.5 correlations",
        "",
    ]
    for name, value in summary["top_correlations"].items():
        lines.append(f"- {name}: {value}")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "Correlation is not causation. Weather variables such as wind and humidity can move with PM2.5 because they affect dispersion and particle formation, but the model still needs time-based validation before any claim is made.",
            "",
        ]
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines))
    return output_path


def main() -> None:
    df = load_or_fetch_dataset()
    path = write_eda_report(df)
    print(f"Wrote EDA report to {path}")


if __name__ == "__main__":
    main()
