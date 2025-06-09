import requests.exceptions
from rest_framework.response import Response
from rest_framework.views import APIView

from weather.serializers import ForecastOverrideSerializer, ForecastQuerySerializer, CurrentWeatherQuerySerializer
from weather.services import get_current_weather, get_forecast_weather
from weather_api.models import WeatherOverride


# Create your views here.
class CurrentWeatherView(APIView):
    """
        GET /api/weather/current?city={city}
        Returns the current temperature and local time for the specified city.
    """
    def get(self, request) -> Response:
        serializer = CurrentWeatherQuerySerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        city = serializer.validated_data["city"]

        try:
            return Response(get_current_weather(city))
        except (requests.exceptions.HTTPError, ValueError) as e:
            return Response({'error': str(e)}, status=503)


class ForecastWeatherView(APIView):
    """
       GET /api/weather/forecast?city={city}&date={dd.MM.yyyy}
       Returns forecast (min/max temperature) for a specific date and city.

       POST /api/weather/forecast
       Overrides forecast for the given city and date.
    """
    def get(self, request) -> Response:
        serializer = ForecastQuerySerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        city = serializer.validated_data["city"]
        date_obj = serializer.validated_data["date"]

        override = WeatherOverride.objects.filter(city=city, date=date_obj).first()

        if override:
            return Response({
                "min_temperature": override.min_temperature,
                "max_temperature": override.max_temperature
            })

        try:
            return Response(get_forecast_weather(city, date_obj))
        except (requests.exceptions.HTTPError, ValueError) as e:
            return Response({'error': str(e)}, status=503)

    def post(self, request) -> Response:
        serializer = ForecastOverrideSerializer(data=request.data)
        if serializer.is_valid():
            WeatherOverride.objects.update_or_create(
                city=serializer.validated_data['city'],
                date=serializer.validated_data['date'],
                defaults={
                    "min_temperature": serializer.validated_data["min_temperature"],
                    "max_temperature": serializer.validated_data["max_temperature"]
                }
            )
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)
