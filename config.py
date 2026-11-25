"""Project-wide settings for LahoreSmog.

Keeping constants in one file makes the project easier to explain in a viva:
if a threshold or coordinate changes, it changes in exactly one place.
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
MODEL_DIR = PROJECT_ROOT / "models"
LOG_DIR = PROJECT_ROOT / "logs"

# Lahore city centre coordinates, used as the default weather location.
LAHORE_LATITUDE = 31.5204
LAHORE_LONGITUDE = 74.3587

# Forecast horizons required by the project brief, in hours.
FORECAST_HORIZONS_HOURS = [1, 6, 12, 24]

# Alert when forecast AQI reaches Unhealthy for Sensitive Groups.
ALERT_AQI_THRESHOLD = 101

# Socket stream interval for the serving phase.
SOCKET_PUSH_INTERVAL_SECONDS = 10
