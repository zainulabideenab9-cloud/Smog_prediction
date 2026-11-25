#!/bin/sh
set -eu

# Deployment containers start without local data/model files because those are
# gitignored. Build them once on startup so the web app has live payloads.
if [ ! -f data/raw/lahore_hourly.csv ]; then
  python -m src.data_fetch --past-days 90 --forecast-days 1
fi

if [ ! -f models/lahoresmog_models.pkl ]; then
  python -m src.modeling
fi

exec uvicorn src.api:app --host 0.0.0.0 --port "${PORT:-8000}"
