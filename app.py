"""Streamlit dashboard for LahoreSmog.

Run locally with:
    streamlit run app.py
"""

from __future__ import annotations

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.dashboard_data import aqi_color, dashboard_frames
from src.modeling import feature_importance
from src.prediction_service import load_models


def main() -> None:
    st.set_page_config(page_title="LahoreSmog", layout="wide")
    st.title("LahoreSmog — AQI prediction and alerts")
    st.caption("Open-Meteo modelled estimates for Lahore. Train the model before relying on forecasts.")

    try:
        current, forecast, stations = dashboard_frames()
    except FileNotFoundError:
        st.error("Fetch data first: python -m src.data_fetch --past-days 90 --forecast-days 1")
        return

    st.metric("Current AQI", current["aqi"], current["category"])
    st.write(f"PM2.5: {current['pm25']} ug/m3 · Last updated: {current['timestamp']}")
    st.caption("Live ticker: backend WebSocket stream at ws://127.0.0.1:8000/ws/predictions; the web app consumes this stream continuously.")

    gauge = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=current["aqi"],
            title={"text": "Current AQI"},
            gauge={"axis": {"range": [0, 500]}, "bar": {"color": aqi_color(current["aqi"])}},
        )
    )
    st.plotly_chart(gauge, use_container_width=True)

    if not forecast.empty:
        fig = px.line(forecast, x="timestamp", y="aqi", markers=True, title="24h AQI forecast")
        fig.add_hline(y=101, line_dash="dash", annotation_text="Sensitive groups threshold")
        fig.add_hline(y=151, line_dash="dash", annotation_text="Unhealthy threshold")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(forecast, use_container_width=True)

    if not stations.empty:
        st.subheader("Lahore zones")
        station_map = px.scatter_mapbox(
            stations,
            lat="latitude",
            lon="longitude",
            color="color",
            hover_name="name",
            zoom=10,
            height=420,
            title="Colour-coded Lahore zones",
        )
        station_map.update_layout(mapbox_style="open-street-map", margin={"r": 0, "t": 40, "l": 0, "b": 0})
        st.plotly_chart(station_map, use_container_width=True)
        st.dataframe(stations, use_container_width=True)

    trained = load_models()
    importance = feature_importance(trained, "24h") if trained else []
    if importance:
        st.subheader("24h feature importance")
        st.bar_chart({name: value for name, value in importance})


if __name__ == "__main__":
    main()
