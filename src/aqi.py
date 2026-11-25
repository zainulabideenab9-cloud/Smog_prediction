"""AQI conversion helpers.

The project predicts PM2.5 first, then converts PM2.5 to AQI for display and
alerts. These breakpoints follow the commonly used US EPA PM2.5 AQI scale.
"""

from __future__ import annotations

# Each tuple is: (pm25_low, pm25_high, aqi_low, aqi_high, category)
PM25_BREAKPOINTS = [
    (0.0, 12.0, 0, 50, "Good"),
    (12.1, 35.4, 51, 100, "Moderate"),
    (35.5, 55.4, 101, 150, "Unhealthy for Sensitive Groups"),
    (55.5, 150.4, 151, 200, "Unhealthy"),
    (150.5, 250.4, 201, 300, "Very Unhealthy"),
    (250.5, 500.4, 301, 500, "Hazardous"),
]


def pm25_to_aqi(pm25: float) -> int:
    """Convert PM2.5 concentration in ug/m3 to AQI.

    AQI uses linear interpolation inside each breakpoint band. Values above the
    highest breakpoint are capped at 500 for display purposes.
    """
    if pm25 < 0:
        raise ValueError("PM2.5 cannot be negative")
    if pm25 > 500.4:
        return 500

    for pm_low, pm_high, aqi_low, aqi_high, _category in PM25_BREAKPOINTS:
        if pm_low <= pm25 <= pm_high:
            aqi = ((aqi_high - aqi_low) / (pm_high - pm_low)) * (pm25 - pm_low) + aqi_low
            return int(round(aqi))

    # PM2.5 values can fall in tiny gaps such as 12.05 because the published
    # bands are rounded to one decimal place. Treat those as the next band.
    for pm_low, _pm_high, aqi_low, _aqi_high, _category in PM25_BREAKPOINTS:
        if pm25 < pm_low:
            return aqi_low
    return 500


def aqi_category(aqi: int) -> str:
    """Return the health category for an AQI value."""
    if aqi < 0:
        raise ValueError("AQI cannot be negative")
    if aqi <= 50:
        return "Good"
    if aqi <= 100:
        return "Moderate"
    if aqi <= 150:
        return "Unhealthy for Sensitive Groups"
    if aqi <= 200:
        return "Unhealthy"
    if aqi <= 300:
        return "Very Unhealthy"
    return "Hazardous"


def pm25_category(pm25: float) -> str:
    """Return the AQI category directly from PM2.5."""
    return aqi_category(pm25_to_aqi(pm25))
