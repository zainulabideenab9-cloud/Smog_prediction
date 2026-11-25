import tempfile
import unittest
from pathlib import Path

import pandas as pd

from src.eda import summarise_dataset, write_eda_report


class EdaTest(unittest.TestCase):
    def test_summary_and_report(self):
        df = pd.DataFrame(
            {
                "timestamp": pd.date_range("2026-11-01", periods=48, freq="h"),
                "pm2_5": [80 + i for i in range(48)],
                "temperature_2m": [15] * 48,
                "relative_humidity_2m": [70] * 48,
                "wind_speed_10m": [5] * 48,
            }
        )
        summary = summarise_dataset(df)
        self.assertEqual(summary["rows"], 48)
        self.assertEqual(summary["missing_after_cleaning"], 0)
        with tempfile.TemporaryDirectory() as tmp:
            path = write_eda_report(df, Path(tmp) / "eda.md")
            self.assertIn("EDA summary", path.read_text())


if __name__ == "__main__":
    unittest.main()
