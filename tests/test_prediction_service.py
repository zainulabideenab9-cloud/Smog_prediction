import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd

from src.prediction_service import current_payload, forecast_payload, load_latest_frame, stations_payload


class PredictionServiceTest(unittest.TestCase):
    def setUp(self):
        self.frame = pd.DataFrame(
            {
                "timestamp": pd.to_datetime(["2026-11-25 10:00"]),
                "pm2_5": [160.0],
            }
        )

    def test_current_payload(self):
        payload = current_payload(self.frame)
        self.assertEqual(payload["pm25"], 160.0)
        self.assertGreater(payload["aqi"], 200)

    def test_forecast_payload_uses_persistence_without_models(self):
        payload = forecast_payload(24, frame=self.frame, models={})
        self.assertEqual(len(payload["forecast"]), 4)
        self.assertEqual(payload["forecast"][0]["pm25"], 160.0)

    def test_stations_payload(self):
        self.assertIn("stations", stations_payload())

    def test_load_latest_frame_falls_back_to_live_fetch(self):
        timestamps = pd.date_range("2026-11-22", periods=96, freq="h")
        raw = pd.DataFrame(
            {
                "timestamp": timestamps,
                "pm2_5": [120.0] * len(timestamps),
                "pm10": [180.0] * len(timestamps),
                "carbon_monoxide": [900.0] * len(timestamps),
                "nitrogen_dioxide": [40.0] * len(timestamps),
                "sulphur_dioxide": [12.0] * len(timestamps),
                "ozone": [30.0] * len(timestamps),
                "temperature_2m": [20.0] * len(timestamps),
                "relative_humidity_2m": [65.0] * len(timestamps),
                "wind_speed_10m": [5.0] * len(timestamps),
                "wind_direction_10m": [180.0] * len(timestamps),
                "precipitation": [0.0] * len(timestamps),
                "surface_pressure": [1015.0] * len(timestamps),
            }
        )
        with patch("src.prediction_service.RAW_DATA_DIR", Path("/tmp/lahoresmog-missing-data")), patch(
            "src.prediction_service.fetch_lahore_dataset", return_value=raw
        ):
            frame = load_latest_frame()
        self.assertFalse(frame.empty)
        self.assertEqual(float(frame.iloc[-1]["pm2_5"]), 120.0)


if __name__ == "__main__":
    unittest.main()
