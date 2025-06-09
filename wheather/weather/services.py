from __future__ import annotations
from rest_framework.exceptions import APIException

from typing import Tuple, Dict

import requests
from decouple import config
from datetime import datetime, timedelta

from requests import Timeout, HTTPError, RequestException

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
    data = fetch_external_api_data(URL_GEO, params)
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
    data = fetch_external_api_data(URL_WEATHER, params)
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

    raise ValueError("Service didn't provide weather on this date")


def fetch_external_api_data(url, params):
    """
       Sends a GET request to an external API with the given URL and parameters.
       Handles timeouts, HTTP errors, and general request exceptions.

       Returns:
           - Parsed JSON response (dict) on success
           - Tuple (error message dict, HTTP status code) on failure
       """
    try:
        resp = requests.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()
    except Timeout:
        # External API took too long
        raise APIException(detail='Upstream API timeout', code=503)
    except HTTPError as http_err:
        # Upstream API returned 4xx or 5xx
        raise APIException(detail=f'Upstream API error: {str(http_err)}', code=503)
    except RequestException as req_err:
        # Catch-all for other issues (DNS failure, connection errors)
        raise APIException(detail=f'Request failed: {str(req_err)}', code=503)
    return data
