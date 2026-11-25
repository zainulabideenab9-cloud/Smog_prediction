# EDA summary

- Rows after hourly cleaning: 744
- Time range: 2026-10-26 00:00:00 to 2026-11-25 23:00:00
- PM2.5 mean: 99.77 ug/m3
- PM2.5 median: 91.5 ug/m3
- PM2.5 maximum: 265.4 ug/m3 (AQI 313)
- Worst average hour: 23:00
- Best average hour: 15:00
- Missing cells after cleaning: 0

## Strongest PM2.5 correlations

- pm10: 0.959
- nitrogen_dioxide: 0.695
- sulphur_dioxide: 0.629
- ozone: -0.582
- relative_humidity_2m: 0.55

## Interpretation

Correlation is not causation. Weather variables such as wind and humidity can move with PM2.5 because they affect dispersion and particle formation, but the model still needs time-based validation before any claim is made.
