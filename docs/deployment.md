# Deployment

## Local web app

```bash
pip install -r requirements-full.txt
python -m src.data_fetch --past-days 90 --forecast-days 1
python -m src.modeling
uvicorn src.api:app --reload
```

Open `http://127.0.0.1:8000`.

## Docker

```bash
docker build -t lahoresmog .
docker run -p 8000:8000 lahoresmog
```

The container start script fetches data and trains the model if local data/model files are missing, then starts FastAPI.

## Render

`render.yaml` defines a Docker web service with `/health` as the health-check path. Connect the GitHub repository in Render and deploy the `main` branch.

## Vercel

Vercel uses `api/index.py` as the FastAPI entrypoint and `vercel.json` to route requests to it. Because serverless deployments do not keep local CSV/model files, the API falls back to a live Open-Meteo fetch and persistence forecasting when local artifacts are missing. The trained-model path remains available locally and in Docker after running the data-fetch and modelling commands.
