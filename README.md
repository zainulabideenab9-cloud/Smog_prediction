# LahoreSmog

LahoreSmog is an AQI prediction and alert system for Lahore. It predicts PM2.5 concentration and AQI category, compares models against a persistence baseline, serves forecasts through an API and socket stream, and presents results in a local dashboard.

## Build plan

This project is built in chunks:

0. Scaffold, configuration, and AQI utilities
1. Data fetching and station coverage checks
2. Preprocessing, feature engineering, and DSA components
3. Exploratory analysis and data quality report
4. Modelling with persistence baseline and honest evaluation
5. FastAPI service and socket prediction stream
6. Streamlit dashboard
7. Alerting with deduplication
8. Documentation and submission pack

## Phase 0 test

```bash
python -m unittest discover -s tests
```

Expected result: all tests pass. This proves the AQI conversion and category logic work before data and modelling are added.

## Constraints

- Python 3.11
- pandas, numpy, scikit-learn, requests, Streamlit, Plotly, FastAPI
- Runs on an 8 GB RAM laptop with no GPU
- No paid APIs and no cloud dependency
