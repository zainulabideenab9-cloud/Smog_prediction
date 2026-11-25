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

## Residual analysis (best model per horizon)

- 1h: mean residual 2.351, std 10.961, max underprediction 81.921, severe missed hours 6/54
- 6h: mean residual 9.169, std 34.769, max underprediction 107.272, severe missed hours 38/57
- 12h: mean residual 10.749, std 44.056, max underprediction 124.907, severe missed hours 53/55
- 24h: mean residual 13.529, std 45.65, max underprediction 160.004, severe missed hours 54/54

## Honest failure note

The model is weakest when pollution changes abruptly, such as stubble-burning episodes, sudden wind shifts, rain washout, or winter inversion nights. Persistence is hard to beat at short horizons because PM2.5 is autocorrelated; if the skill score is near zero or negative, the model is not yet better than assuming tomorrow looks like today.
