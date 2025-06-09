from __future__ import annotations

from typing import Tuple, Dict

import requests
from decouple import config
from datetime import datetime, timedelta

API_KEY = config("OPENWEATHER_API_KEY")
URL_WEATHER = "https://api.openweathermap.org/data/3.0/onecall"
URL_GEO = "https://api.openweathermap.org/geo/1.0/direct"


def get_coordinates(city: str) -> Tuple[float, float]:
    """
        Resolve city name to geographic coordinates using OpenWeather Geocoding API.

        Raises:
            ValueError: If the city is not found.
        Returns:
            tuple: (latitude, longitude)
    """
    params = {"q": city, "limit": 1, "appid": API_KEY}
    resp = requests.get(URL_GEO, params=params)
    resp.raise_for_status()
    data = resp.json()
    if not data:
        raise ValueError("City not found")
    return data[0]["lat"], data[0]["lon"]


def get_weather_information(city: str) -> Dict:
    """
       Fetch full weather data using One Call API 3.0 by city name.

       Returns:
           dict: Full JSON response including current and daily forecast data.
    """
    lat, lon = get_coordinates(city)
    params = {
        "lat": lat,
        "lon": lon,
        "units": "metric",
        "appid": API_KEY
    }
    resp = requests.get(URL_WEATHER, params=params)
    resp.raise_for_status()
    data = resp.json()
    if not data:
        raise ValueError("Weather not found")
    return data


def get_current_weather(city: str) -> Dict[str, str | float]:
    """
        Extract current temperature and local time from weather data.

        Returns:
            dict: { "temperature": float, "local_time": "HH:MM" }
    """
    data = get_weather_information(city)

    # Apply timezone offset
    timestamp = data["current"]["dt"] + data.get("timezone_offset", 0)
    local_time = datetime.utcfromtimestamp(timestamp).strftime("%H:%M")

    return {
        "temperature": round(data["current"]["temp"], 1),
        "local_time": local_time
    }


def get_forecast_weather(city: str, target_date: datetime.date) -> Dict[str, float]:
    """
        Get min/max forecast temperatures for a specific future date (max 10 days ahead).

        Raises:
            ValueError: If forecast for target date is not available.
        Returns:
            dict: { "min_temperature": float, "max_temperature": float }
    """
    data = get_weather_information(city)

    for day in data.get("daily", []):
        forecast_date = datetime.utcfromtimestamp(day["dt"]).date()
        if forecast_date == target_date:
            return {
                "min_temperature": round(day["temp"]["min"], 1),
                "max_temperature": round(day["temp"]["max"], 1)
            }

    raise ValueError("Forecast not available for this date (only 10 days ahead)")