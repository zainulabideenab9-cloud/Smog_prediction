# Presentation outline

1. **Problem** — Lahore smog, PM2.5, AQI, and why early warning matters
2. **Data** — Open-Meteo hourly air quality + weather, coverage checks, limitations
3. **Preprocessing** — hourly alignment, interpolation, lag and rolling features
4. **DSA components** — sliding window, priority queue, BFS zone traversal
5. **Modelling** — persistence baseline, linear regression, random forest, gradient boosting
6. **Results** — RMSE, MAE, R², skill versus persistence by horizon
7. **System demo** — FastAPI, WebSocket stream, Streamlit dashboard, alerts
8. **Limitations and future work** — official station data, probabilistic forecasts, public deployment
