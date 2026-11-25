# Requirements checklist

| Requirement | Evidence |
|---|---|
| Predict PM2.5 and AQI category for Lahore | `src/aqi.py`, `src/prediction_service.py`, `reports/model_results.md` |
| Time-based split, never random shuffle | `src/modeling.py` `time_split` and `tests/test_modeling.py` |
| Persistence baseline | `src/modeling.py` persistence metrics and skill score |
| Linear regression, random forest, gradient boosting | `src/modeling.py` `candidate_models` |
| Metrics per 1h, 6h, 12h, 24h horizon | `reports/model_results.md`, `reports/model_metrics.json` |
| Feature importance | `reports/model_results.md` 24h feature importance section |
| Residual analysis | `reports/model_results.md` residual analysis section |
| Honest failure paragraph | `reports/model_results.md` honest failure note |
| FastAPI endpoints | `src/api.py`: `/current`, `/forecast`, `/stations`, `/health` |
| WebSocket stream and client | `src/api.py` `/ws/predictions`, `src/socket_client.py`, `static/app.js` |
| Web app backend | `src/api.py` serves `static/index.html` at `/` |
| Streamlit dashboard | `app.py`: gauge, 24h chart, threshold bands, colour-coded zone map, feature importance, live ticker note |
| Alerting with deduplication | `src/alerts.py`, `tests/test_alerts.py` |
| README and submission pack | `README.md`, `docs/one_page_summary.md`, `docs/demo_script.md`, `docs/presentation_outline.md` |
| No paid APIs or cloud dependency | Open-Meteo free APIs, local FastAPI/Streamlit execution |
