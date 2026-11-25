"""Alerting for LahoreSmog forecasts.

Alerts are written to a local JSON-lines log. Email is optional and disabled by
default because the project must not depend on paid services or credentials.
"""

from __future__ import annotations

import json
from pathlib import Path

from config import ALERT_AQI_THRESHOLD, LOG_DIR
from src.dsa import AlertPriorityQueue
from src.prediction_service import forecast_payload

ALERT_LOG_PATH = LOG_DIR / "alerts.jsonl"


def alert_key(alert: dict) -> str:
    """Return the deduplication key for one forecast hour."""
    return f"{alert['timestamp']}|{alert['horizon_hours']}|{alert['aqi']}"


def build_alerts(forecast: list[dict], threshold: int = ALERT_AQI_THRESHOLD) -> list[dict]:
    """Build alerts for forecast points at or above the AQI threshold."""
    queue = AlertPriorityQueue()
    for point in forecast:
        if int(point["aqi"]) >= threshold:
            queue.push(
                {
                    "timestamp": point["timestamp"],
                    "horizon_hours": point["horizon_hours"],
                    "pm25": point["pm25"],
                    "aqi": point["aqi"],
                    "category": point["category"],
                    "message": f"Lahore AQI forecast {point['aqi']} ({point['category']}) at {point['timestamp']}",
                }
            )
    alerts = []
    while len(queue):
        alerts.append(queue.pop())
    return alerts


def load_sent_keys(log_path: Path = ALERT_LOG_PATH) -> set[str]:
    """Load alert keys already written to the local log."""
    if not log_path.exists():
        return set()
    keys = set()
    for line in log_path.read_text().splitlines():
        if line.strip():
            keys.add(alert_key(json.loads(line)))
    return keys


def write_new_alerts(alerts: list[dict], log_path: Path = ALERT_LOG_PATH) -> list[dict]:
    """Write only alerts that have not fired before."""
    sent = load_sent_keys(log_path)
    new_alerts = [alert for alert in alerts if alert_key(alert) not in sent]
    if new_alerts:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("a") as handle:
            for alert in new_alerts:
                handle.write(json.dumps(alert) + "\n")
    return new_alerts


def main() -> None:
    forecast = forecast_payload(24)["forecast"]
    alerts = build_alerts(forecast)
    new_alerts = write_new_alerts(alerts)
    print(f"Forecast alerts above threshold: {len(alerts)}")
    print(f"New alerts written: {len(new_alerts)}")
    for alert in new_alerts:
        print(alert["message"])


if __name__ == "__main__":
    main()
