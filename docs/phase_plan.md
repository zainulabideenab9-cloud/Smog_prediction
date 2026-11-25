# LahoreSmog phase plan

## Chunk 0 — Scaffold
Repo structure, configuration, AQI conversion, and smoke tests.

## Chunk 1 — Data
Fetch Lahore air-quality and weather data. Check station coverage first. If OpenAQ coverage is patchy, shift to Open-Meteo plus NASA POWER daily data.

## Chunk 2 — Preprocessing and DSA
Clean time series, align timestamps, engineer lag and rolling features, and add DSA components such as a sliding window, priority queue for alerts, and graph-based station neighbourhoods.

## Chunk 3 — EDA
Data quality report, missing-value analysis, seasonal plots, and correlation checks.

## Chunk 4 — Modelling
Time-based split, persistence baseline, linear regression, random forest, gradient boosting, metrics per horizon, feature importance, residual analysis, and honest failure notes.

## Chunk 5 — Serving
FastAPI endpoints for current conditions, forecasts, and stations, plus a WebSocket stream and client script.

## Chunk 6 — Dashboard
Streamlit dashboard with AQI gauge, forecast chart, category bands, station map, feature importance, and live ticker.

## Chunk 7 — Alerting
Threshold alerts with deduplication and local logging.

## Chunk 8 — Submission pack
README completion, one-page summary, demo script, and presentation outline.
