import tempfile
import unittest
from pathlib import Path

from src.alerts import build_alerts, write_new_alerts


class AlertsTest(unittest.TestCase):
    def test_build_alerts_threshold_and_priority(self):
        forecast = [
            {"timestamp": "2026-11-26 00:00", "horizon_hours": 1, "pm25": 80, "aqi": 160, "category": "Unhealthy"},
            {"timestamp": "2026-11-26 06:00", "horizon_hours": 6, "pm25": 40, "aqi": 90, "category": "Moderate"},
            {"timestamp": "2026-11-26 12:00", "horizon_hours": 12, "pm25": 180, "aqi": 230, "category": "Very Unhealthy"},
        ]
        alerts = build_alerts(forecast)
        self.assertEqual(len(alerts), 2)
        self.assertEqual(alerts[0]["aqi"], 230)

    def test_deduplication(self):
        alerts = build_alerts(
            [{"timestamp": "2026-11-26 00:00", "horizon_hours": 1, "pm25": 80, "aqi": 160, "category": "Unhealthy"}]
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "alerts.jsonl"
            self.assertEqual(len(write_new_alerts(alerts, path)), 1)
            self.assertEqual(len(write_new_alerts(alerts, path)), 0)


if __name__ == "__main__":
    unittest.main()
