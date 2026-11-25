import unittest

import pandas as pd

from src.dsa import AlertPriorityQueue, SlidingWindowMean, bfs_zone_order
from src.features import build_feature_frame, feature_columns


def sample_frame(rows: int = 80) -> pd.DataFrame:
    timestamps = pd.date_range("2026-11-01", periods=rows, freq="h")
    return pd.DataFrame(
        {
            "timestamp": timestamps,
            "pm2_5": [100 + i for i in range(rows)],
            "pm10": [140 + i for i in range(rows)],
            "carbon_monoxide": [900] * rows,
            "nitrogen_dioxide": [40] * rows,
            "sulphur_dioxide": [12] * rows,
            "ozone": [30] * rows,
            "temperature_2m": [15] * rows,
            "relative_humidity_2m": [70] * rows,
            "wind_speed_10m": [5] * rows,
            "wind_direction_10m": [90] * rows,
            "precipitation": [0] * rows,
            "surface_pressure": [1015] * rows,
        }
    )


class FeatureTest(unittest.TestCase):
    def test_feature_frame_has_targets_and_no_missing(self):
        frame = build_feature_frame(sample_frame())
        self.assertIn("target_pm25_24h", frame.columns)
        self.assertIn("pm25_lag_24h", feature_columns(frame))
        self.assertFalse(frame[feature_columns(frame)].isna().any().any())

    def test_sliding_window_mean(self):
        window = SlidingWindowMean(3)
        self.assertEqual(window.add(10), 10)
        self.assertEqual(window.add(20), 15)
        self.assertEqual(window.add(30), 20)
        self.assertEqual(window.add(40), 30)

    def test_alert_priority_queue(self):
        queue = AlertPriorityQueue()
        queue.push({"aqi": 120, "zone": "Gulberg"})
        queue.push({"aqi": 220, "zone": "Shahdara"})
        self.assertEqual(queue.pop()["zone"], "Shahdara")

    def test_bfs_zone_order(self):
        graph = {"Gulberg": ["DHA", "Model Town"], "DHA": ["Johar Town"]}
        self.assertEqual(bfs_zone_order(graph, "Gulberg"), ["Gulberg", "DHA", "Model Town", "Johar Town"])


if __name__ == "__main__":
    unittest.main()
