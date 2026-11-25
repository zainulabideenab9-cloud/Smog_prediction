import unittest
from pathlib import Path

from src.api import app, health


class WebAppBackendTest(unittest.TestCase):
    def test_health_payload(self):
        self.assertEqual(health()["status"], "ok")

    def test_web_app_routes_exist(self):
        paths = {route.path for route in app.routes}
        self.assertIn("/", paths)
        self.assertIn("/health", paths)
        self.assertIn("/current", paths)
        self.assertIn("/forecast", paths)
        self.assertIn("/ws/predictions", paths)

    def test_static_files_exist(self):
        root = Path(__file__).resolve().parents[1]
        self.assertTrue((root / "static" / "index.html").exists())
        self.assertTrue((root / "static" / "app.js").exists())
        self.assertTrue((root / "static" / "styles.css").exists())
        index = (root / "static" / "index.html").read_text()
        app_js = (root / "static" / "app.js").read_text()
        self.assertIn("aqi-gauge", index)
        self.assertIn("health-advice", index)
        self.assertIn("adviceForAqi", app_js)

    def test_deployment_files_exist(self):
        root = Path(__file__).resolve().parents[1]
        self.assertTrue((root / "Dockerfile").exists())
        self.assertTrue((root / "render.yaml").exists())
        self.assertTrue((root / "scripts" / "start.sh").exists())
        self.assertTrue((root / "vercel.json").exists())
        self.assertTrue((root / "api" / "index.py").exists())
        self.assertTrue((root / "requirements-full.txt").exists())


if __name__ == "__main__":
    unittest.main()
