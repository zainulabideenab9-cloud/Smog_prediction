import unittest

import numpy as np
import pandas as pd

from src.features import build_feature_frame
from src.modeling import metric_bundle, time_split, train_and_evaluate


def sample_frame(rows: int = 240) -> pd.DataFrame:
    rng = np.random.default_rng(7)
    pm25 = 90 + np.cumsum(rng.normal(0, 2, rows)).clip(-40, 90)
    return pd.DataFrame(
        {
            "timestamp": pd.date_range("2026-10-01", periods=rows, freq="h"),
            "pm2_5": pm25,
            "pm10": pm25 * 1.4,
            "carbon_monoxide": 900 + pm25,
            "nitrogen_dioxide": 30 + pm25 / 5,
            "sulphur_dioxide": 10 + pm25 / 20,
            "ozone": 40 - pm25 / 10,
            "temperature_2m": 16 + np.sin(np.arange(rows) / 24),
            "relative_humidity_2m": 65 + pm25 / 10,
            "wind_speed_10m": 6 - pm25 / 100,
            "wind_direction_10m": 90,
            "precipitation": 0,
            "surface_pressure": 1015,
        }
    )


class ModelingTest(unittest.TestCase):
    def test_time_split_preserves_order(self):
        frame = build_feature_frame(sample_frame())
        train, validation, test = time_split(frame)
        self.assertLess(train["timestamp"].max(), validation["timestamp"].min())
        self.assertLess(validation["timestamp"].max(), test["timestamp"].min())

    def test_metric_bundle_skill(self):
        metrics = metric_bundle(np.array([100.0, 120.0]), np.array([100.0, 120.0]), np.array([90.0, 90.0]))
        self.assertEqual(metrics["rmse"], 0.0)
        self.assertEqual(metrics["skill_vs_persistence"], 1.0)

    def test_train_and_evaluate_returns_horizons(self):
        frame = build_feature_frame(sample_frame())
        results, trained = train_and_evaluate(frame)
        self.assertIn("24h", results)
        self.assertIn("best_model", results["24h"])
        self.assertIn("residual_analysis", results["24h"])
        self.assertIn("24h", trained)


if __name__ == "__main__":
    unittest.main()
