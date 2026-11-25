# LahoreSmog

### Predict Lahore’s smog before it settles in.

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Pandas-Data-150458?style=for-the-badge&logo=pandas&logoColor=white" alt="Pandas">
  <img src="https://img.shields.io/badge/scikit--learn-ML-F7931E?style=for-the-badge&logo=scikitlearn&logoColor=white" alt="scikit-learn">
  <img src="https://img.shields.io/badge/FastAPI-API-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit">
  <img src="https://img.shields.io/badge/Plotly-Charts-3F4F75?style=for-the-badge&logo=plotly&logoColor=white" alt="Plotly">
</p>

**LahoreSmog** is an end-to-end AQI prediction and alert system for Lahore. It forecasts PM2.5 and AQI category at **1h, 6h, 12h, and 24h** horizons, beats a persistence baseline honestly, streams live predictions over WebSocket, and turns the forecast into a dashboard and alerts.

> Built for a laptop. No GPU. No paid APIs. No cloud dependency.

---

## Quick start

```bash
pip install -r requirements.txt
python -m src.data_fetch --past-days 90 --forecast-days 1
python -m src.eda
python -m src.modeling
uvicorn src.api:app --reload
# open http://127.0.0.1:8000 for the web app
streamlit run app.py
```

Run tests:

```bash
python -m unittest discover -s tests
```

Deployment notes: [`docs/deployment.md`](docs/deployment.md)

---

## Architecture

```text
Open-Meteo hourly data
        ↓
Cleaning + lag/rolling features
        ↓
Time-based modelling vs persistence baseline
        ↓
FastAPI endpoints + WebSocket prediction stream
        ↓
Streamlit dashboard + deduplicated alerts
```

---

## Results snapshot

Latest local run on 90 days of hourly Open-Meteo data:

| Horizon | Best model | RMSE | MAE | R² | Persistence RMSE | Skill |
|---|---|---:|---:|---:|---:|---:|
| 1h | Linear regression | 11.21 | 7.13 | 0.9541 | 13.52 | 0.1708 |
| 6h | Linear regression | 35.96 | 27.60 | 0.5396 | 49.76 | 0.2773 |
| 12h | Linear regression | 45.35 | 35.09 | 0.2765 | 62.04 | 0.2691 |
| 24h | Random forest | 47.61 | 36.02 | 0.2205 | 60.49 | 0.2129 |

Skill score is measured against persistence: **tomorrow equals today**. Positive skill means the model beat that baseline on the most recent test block.

Full report: [`reports/model_results.md`](reports/model_results.md)

---

## What makes it honest

- **Time-based split only** — train on older data, test on the most recent period.
- **Persistence baseline first** — the model must beat “next PM2.5 equals current PM2.5”.
- **Coverage is printed** — missing PM2.5 data is reported, not hidden.
- **Data limitation stated** — Open-Meteo air-quality values are modelled/gridded estimates, not official Lahore reference-station observations.

---

## DSA inside the project

| Component | Where | Complexity |
|---|---|---|
| Sliding-window mean | `src/dsa.py` | O(1) amortised update |
| Alert priority queue | `src/dsa.py` | O(log n) push/pop |
| BFS over Lahore zones | `src/dsa.py` | O(V + E) |
| Lag + rolling features | `src/features.py` | O(n) per feature pass |

---

## Repo map

```text
app.py                         Streamlit dashboard
config.py                      Paths, thresholds, Lahore coordinates
src/aqi.py                     PM2.5 → AQI conversion
src/data_fetch.py              Open-Meteo fetch + coverage report
src/preprocess.py              Hourly cleaning and time features
src/features.py                Lag, rolling, and target features
src/modeling.py                Models, metrics, persistence skill
src/prediction_service.py      Shared prediction payloads
src/api.py                     FastAPI + WebSocket stream
src/alerts.py                  Threshold alerts with deduplication
reports/eda_summary.md         EDA and data-quality summary
reports/model_results.md       Model results and failure note
docs/                          Data sources and submission pack
tests/                         Unit tests for every chunk
```

---

## Alerts

Alerts fire when forecast AQI reaches **101+** and are deduplicated by timestamp, horizon, and AQI value.

```bash
python -m src.alerts
```

---

## Limitations

- Open-Meteo is a practical free source, but official station data would be stronger.
- Abrupt stubble-burning episodes, rain washout, and inversion nights remain hard to predict.
- The current zones are mapping zones, not claimed official monitoring stations.

## Future work

- Add official Punjab EPA / PMD / OpenAQ station exports
- Add 3-day probabilistic forecasts
- Add school and hospital alert modes
- Compare against gradient boosting with tuned hyperparameters
- Deploy a public read-only dashboard

---

**LahoreSmog — because “AQI is bad today” is too late. Predict it earlier.**
