# Model results

| Horizon | Best model | RMSE | MAE | R2 | Persistence RMSE | Skill |
|---|---|---:|---:|---:|---:|---:|
| 1h | linear_regression | 11.21 | 7.131 | 0.9541 | 13.518 | 0.1708 |
| 6h | linear_regression | 35.958 | 27.595 | 0.5396 | 49.756 | 0.2773 |
| 12h | linear_regression | 45.349 | 35.087 | 0.2765 | 62.044 | 0.2691 |
| 24h | random_forest | 47.612 | 36.022 | 0.2205 | 60.488 | 0.2129 |

## Feature importance (24h best model)

- pm2_5: 0.3762
- ozone: 0.077
- surface_pressure: 0.0422
- pm25_lag_24h: 0.0401
- wind_direction_10m: 0.0398
- pm25_max_24h: 0.0387
- temperature_2m: 0.0372
- pm25_mean_24h: 0.0352
- relative_humidity_2m: 0.0283
- day_of_week: 0.0283

## Honest failure note

The model is weakest when pollution changes abruptly, such as stubble-burning episodes, sudden wind shifts, rain washout, or winter inversion nights. Persistence is hard to beat at short horizons because PM2.5 is autocorrelated; if the skill score is near zero or negative, the model is not yet better than assuming tomorrow looks like today.
