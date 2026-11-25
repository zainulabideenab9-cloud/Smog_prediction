# 2-minute demo script

## Shot 1 — Problem, 0:00–0:20
Show Lahore smog/AQI context. Say: “LahoreSmog predicts PM2.5 and AQI before conditions peak, so people can plan earlier.”

## Shot 2 — Data, 0:20–0:40
Run `python -m src.data_fetch --past-days 90 --forecast-days 1`. Show the coverage report and say coverage is checked before modelling.

## Shot 3 — Model, 0:40–1:05
Run `python -m src.modeling`. Show the results table and persistence skill score. Say the test block is the most recent period, never shuffled.

## Shot 4 — API and socket, 1:05–1:25
Start `uvicorn src.api:app --reload`, open `/docs`, then run `python -m src.socket_client` to show a live prediction payload.

## Shot 5 — Dashboard and alerts, 1:25–2:00
Run `streamlit run app.py`. Show current AQI, 24h forecast, zones, and feature importance. Finish with `python -m src.alerts` and the deduplicated alert log.
