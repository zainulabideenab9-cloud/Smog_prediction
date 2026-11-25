import unittest

import pandas as pd

from src.prediction_service import current_payload, forecast_payload, stations_payload


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


if __name__ == "__main__":
    unittest.main()
