import unittest

import pandas as pd

from src.data_fetch import _hourly_to_frame, coverage_report, merge_hourly
from src.stations import zone_names


class DataFetchTest(unittest.TestCase):
    def test_hourly_payload_parsing(self):
        payload = {
            "hourly": {
                "time": ["2026-11-25T00:00", "2026-11-25T01:00"],
                "pm2_5": [120.0, 135.0],
            }
        }
        frame = _hourly_to_frame(payload, ["pm2_5"])
        self.assertEqual(len(frame), 2)
        self.assertEqual(frame.loc[1, "pm2_5"], 135.0)

    def test_merge_and_coverage(self):
        air = pd.DataFrame(
            {
                "timestamp": pd.to_datetime(["2026-11-25 00:00", "2026-11-25 01:00"]),
                "pm2_5": [120.0, None],
            }
        )
        weather = pd.DataFrame(
            {
                "timestamp": pd.to_datetime(["2026-11-25 00:00", "2026-11-25 01:00"]),
                "temperature_2m": [14.0, 13.0],
            }
        )
        merged = merge_hourly(air, weather)
        report = coverage_report(merged)
        self.assertEqual(report["rows"], 2)
        self.assertEqual(report["pm25_non_null"], 1)
        self.assertEqual(report["missing_pct"]["pm2_5"], 50.0)

    def test_zone_names_present(self):
        self.assertIn("Gulberg", zone_names())


if __name__ == "__main__":
    unittest.main()
