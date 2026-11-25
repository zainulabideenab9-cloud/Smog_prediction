import unittest

from src.dashboard_data import aqi_color


class DashboardDataTest(unittest.TestCase):
    def test_aqi_colors(self):
        self.assertEqual(aqi_color(40), "green")
        self.assertEqual(aqi_color(120), "orange")
        self.assertEqual(aqi_color(260), "purple")
        self.assertEqual(aqi_color(400), "maroon")


if __name__ == "__main__":
    unittest.main()
