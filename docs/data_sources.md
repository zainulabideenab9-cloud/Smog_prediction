# Data sources

## Primary source for Chunk 1

Open-Meteo Air Quality API and Weather Forecast API are used because they are free, require no API key, and provide hourly variables suitable for a student laptop project.

- Air quality API docs: https://open-meteo.com/en/docs/air-quality-api
- Weather forecast API docs: https://open-meteo.com/en/docs
- Air-quality endpoint used in code: https://air-quality-api.open-meteo.com/v1/air-quality
- Weather endpoint used in code: https://api.open-meteo.com/v1/forecast

- Air quality: PM2.5, PM10, carbon monoxide, nitrogen dioxide, sulphur dioxide, ozone
- Weather: temperature, relative humidity, wind speed, wind direction, precipitation, surface pressure

Important limitation: Open-Meteo air-quality values are modelled/gridded estimates. They are useful for building and demonstrating the pipeline, but they should not be presented as official Lahore reference-station observations.

## Coverage rule

Before modelling, run the fetch script and inspect the coverage report. If PM2.5 coverage is weak or the time range is too short, extend the fetch window or add a daily fallback source such as NASA POWER weather data. Do not hide missing data.

## Future official-data upgrade

If Punjab EPA, PMD, or OpenAQ station data becomes available with a usable export, replace the Open-Meteo air-quality frame with station observations while keeping the same merged column names where possible.
