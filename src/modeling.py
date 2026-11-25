"""Modelling and honest evaluation for LahoreSmog.

Evaluation is time-based: train on older rows, validate on the next block, and
test on the most recent block. Random shuffling would leak future smog patterns
into training and inflate the score.
"""

from __future__ import annotations

import json
import pickle
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from config import FORECAST_HORIZONS_HOURS, MODEL_DIR, PROJECT_ROOT, RAW_DATA_DIR
from src.features import build_feature_frame, feature_columns

RESULTS_PATH = PROJECT_ROOT / "reports" / "model_results.md"
METRICS_PATH = PROJECT_ROOT / "reports" / "model_metrics.json"


def time_split(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Split into train, validation, and test blocks in time order."""
    n = len(df)
    train_end = int(n * 0.7)
    val_end = int(n * 0.85)
    return df.iloc[:train_end], df.iloc[train_end:val_end], df.iloc[val_end:]


def metric_bundle(y_true: np.ndarray, y_pred: np.ndarray, baseline_pred: np.ndarray) -> dict:
    """Return RMSE, MAE, R2, and skill score versus persistence."""
    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    baseline_rmse = float(np.sqrt(mean_squared_error(y_true, baseline_pred)))
    skill = 1 - (rmse / baseline_rmse) if baseline_rmse else 0.0
    return {
        "rmse": round(rmse, 3),
        "mae": round(float(mean_absolute_error(y_true, y_pred)), 3),
        "r2": round(float(r2_score(y_true, y_pred)), 4),
        "persistence_rmse": round(baseline_rmse, 3),
        "skill_vs_persistence": round(float(skill), 4),
    }


def residual_analysis(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    """Summarise residuals for the best model at one horizon.

    Residual = actual - predicted. Positive residuals mean the model
    under-predicted PM2.5, which is the dangerous direction for smog alerts.
    """
    residuals = y_true - y_pred
    severe_actual = y_true >= 150
    severe_missed = severe_actual & (y_pred < 150)
    return {
        "mean_residual": round(float(np.mean(residuals)), 3),
        "residual_std": round(float(np.std(residuals)), 3),
        "max_underprediction": round(float(np.max(residuals)), 3),
        "max_overprediction": round(float(np.min(residuals)), 3),
        "severe_actual_hours": int(severe_actual.sum()),
        "severe_missed_hours": int(severe_missed.sum()),
    }


def candidate_models() -> dict:
    """Return the sklearn models required by the brief."""
    return {
        "linear_regression": LinearRegression(),
        "random_forest": RandomForestRegressor(n_estimators=160, random_state=42, n_jobs=-1),
        "gradient_boosting": GradientBoostingRegressor(random_state=42),
    }


def train_and_evaluate(df: pd.DataFrame) -> tuple[dict, dict]:
    """Train one model per horizon and evaluate on the recent test block."""
    features = feature_columns(df)
    train, _validation, test = time_split(df)
    results: dict[str, dict] = {}
    trained: dict[str, object] = {}

    for horizon in FORECAST_HORIZONS_HOURS:
        target = f"target_pm25_{horizon}h"
        X_train, y_train = train[features], train[target]
        X_test, y_test = test[features], test[target]
        persistence = test["pm2_5"].to_numpy(dtype=float)

        horizon_results = {}
        best_name, best_model, best_rmse, best_predictions = None, None, float("inf"), None
        for name, model in candidate_models().items():
            model.fit(X_train, y_train)
            predictions = np.clip(model.predict(X_test), 0, None)
            metrics = metric_bundle(y_test.to_numpy(dtype=float), predictions, persistence)
            horizon_results[name] = metrics
            if metrics["rmse"] < best_rmse:
                best_name, best_model, best_rmse, best_predictions = name, model, metrics["rmse"], predictions

        horizon_results["persistence"] = metric_bundle(y_test.to_numpy(dtype=float), persistence, persistence)
        horizon_results["residual_analysis"] = residual_analysis(y_test.to_numpy(dtype=float), best_predictions)
        horizon_results["best_model"] = best_name
        results[f"{horizon}h"] = horizon_results
        trained[f"{horizon}h"] = {"model": best_model, "features": features, "model_name": best_name}

    return results, trained


def feature_importance(trained: dict, horizon: str = "24h") -> list[tuple[str, float]]:
    """Return top feature importances when the best model supports them."""
    bundle = trained.get(horizon, {})
    model = bundle.get("model")
    features = bundle.get("features", [])
    if model is None or not hasattr(model, "feature_importances_"):
        return []
    pairs = sorted(zip(features, model.feature_importances_), key=lambda item: item[1], reverse=True)
    return [(name, round(float(value), 4)) for name, value in pairs[:10]]


def write_results(results: dict, trained: dict) -> tuple[Path, Path]:
    """Write metrics JSON and a plain-language results report."""
    METRICS_PATH.parent.mkdir(parents=True, exist_ok=True)
    METRICS_PATH.write_text(json.dumps(results, indent=2) + "\n")

    lines = ["# Model results", "", "| Horizon | Best model | RMSE | MAE | R2 | Persistence RMSE | Skill |", "|---|---|---:|---:|---:|---:|---:|"]
    for horizon, values in results.items():
        best = values["best_model"]
        metrics = values[best]
        lines.append(
            f"| {horizon} | {best} | {metrics['rmse']} | {metrics['mae']} | {metrics['r2']} | {metrics['persistence_rmse']} | {metrics['skill_vs_persistence']} |"
        )
    lines.extend(["", "## Feature importance (24h best model)", ""])
    importance = feature_importance(trained, "24h")
    if importance:
        for name, value in importance:
            lines.append(f"- {name}: {value}")
    else:
        lines.append("- The best 24h model does not expose feature importances.")
    lines.extend(["", "## Residual analysis (best model per horizon)", ""])
    for horizon, values in results.items():
        residual = values["residual_analysis"]
        lines.append(
            f"- {horizon}: mean residual {residual['mean_residual']}, std {residual['residual_std']}, "
            f"max underprediction {residual['max_underprediction']}, severe missed hours "
            f"{residual['severe_missed_hours']}/{residual['severe_actual_hours']}"
        )
    lines.extend(
        [
            "",
            "## Honest failure note",
            "",
            "The model is weakest when pollution changes abruptly, such as stubble-burning episodes, sudden wind shifts, rain washout, or winter inversion nights. Persistence is hard to beat at short horizons because PM2.5 is autocorrelated; if the skill score is near zero or negative, the model is not yet better than assuming tomorrow looks like today.",
            "",
        ]
    )
    RESULTS_PATH.write_text("\n".join(lines))
    return RESULTS_PATH, METRICS_PATH


def save_models(trained: dict) -> Path:
    """Save trained models locally. Pickles are gitignored."""
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    path = MODEL_DIR / "lahoresmog_models.pkl"
    with path.open("wb") as handle:
        pickle.dump(trained, handle)
    return path


def main() -> None:
    raw_path = RAW_DATA_DIR / "lahore_hourly.csv"
    if not raw_path.exists():
        raise SystemExit("Fetch data first: python -m src.data_fetch --past-days 90 --forecast-days 1")
    raw = pd.read_csv(raw_path, parse_dates=["timestamp"])
    frame = build_feature_frame(raw)
    results, trained = train_and_evaluate(frame)
    report_path, metrics_path = write_results(results, trained)
    model_path = save_models(trained)
    print(f"Wrote {report_path}")
    print(f"Wrote {metrics_path}")
    print(f"Saved local models to {model_path}")
    for horizon, values in results.items():
        best = values["best_model"]
        print(f"{horizon}: {best}, skill={values[best]['skill_vs_persistence']}")


if __name__ == "__main__":
    main()
