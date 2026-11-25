import unittest

from src.aqi import aqi_category, pm25_category, pm25_to_aqi


class AqiTest(unittest.TestCase):
    def test_pm25_to_aqi_known_points(self):
        self.assertEqual(pm25_to_aqi(0), 0)
        self.assertEqual(pm25_to_aqi(12.0), 50)
        self.assertEqual(pm25_to_aqi(35.4), 100)
        self.assertEqual(pm25_to_aqi(55.4), 150)
        self.assertEqual(pm25_to_aqi(600), 500)

    def test_categories(self):
        self.assertEqual(aqi_category(50), "Good")
        self.assertEqual(aqi_category(101), "Unhealthy for Sensitive Groups")
        self.assertEqual(pm25_category(160), "Very Unhealthy")

    def test_negative_values_rejected(self):
        with self.assertRaises(ValueError):
            pm25_to_aqi(-1)
        with self.assertRaises(ValueError):
            aqi_category(-5)


if __name__ == "__main__":
    unittest.main()
