# Viva Q&A

## Why predict PM2.5 instead of AQI directly?
PM2.5 is the measured pollutant concentration. AQI is a derived display scale, so the model predicts PM2.5 first and then converts it to AQI for users.

## Why use a time-based split?
Air-quality data is a time series. Random shuffling would leak future pollution patterns into training and make the score look better than real forecasting performance.

## What is the persistence baseline?
Persistence assumes the future PM2.5 equals the current PM2.5. It is simple but strong at short horizons because pollution changes gradually.

## What does skill score mean?
Skill score compares model RMSE with persistence RMSE. Positive skill means the model beat persistence; zero means it matched it; negative means it was worse.

## Why include weather variables?
Wind disperses particles, humidity affects particle growth and visibility, rainfall washes particles out, and temperature/pressure relate to inversion conditions.

## What are the DSA components?
A sliding-window mean for rolling features, a priority queue for severe alerts, and BFS for Lahore zone traversal. Their complexities are documented in the README.

## What is the biggest limitation?
Open-Meteo air-quality values are modelled estimates, not official Lahore station observations. The pipeline is ready for official station exports, but results should be described honestly.

## Where does the model fail?
It struggles during abrupt changes such as stubble-burning episodes, sudden wind shifts, rain washout, and winter inversion nights. Residual analysis in the model report shows underprediction risk during severe hours.
