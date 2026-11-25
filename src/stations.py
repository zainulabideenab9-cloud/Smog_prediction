"""Lahore monitoring zones used by the dashboard and coverage checks.

These are city zones for mapping and explanation. They are not claimed to be
official reference stations. If official station data becomes available, add
the station ID and source here instead of changing dashboard code.
"""

from __future__ import annotations

LAHORE_ZONES = [
    {"name": "Gulberg", "latitude": 31.5102, "longitude": 74.3441},
    {"name": "DHA", "latitude": 31.4697, "longitude": 74.4072},
    {"name": "Johar Town", "latitude": 31.4696, "longitude": 74.2728},
    {"name": "Model Town", "latitude": 31.4805, "longitude": 74.3210},
    {"name": "Shahdara", "latitude": 31.6222, "longitude": 74.2827},
    {"name": "Walled City", "latitude": 31.5889, "longitude": 74.3100},
]


def zone_names() -> list[str]:
    """Return zone names in display order."""
    return [zone["name"] for zone in LAHORE_ZONES]
