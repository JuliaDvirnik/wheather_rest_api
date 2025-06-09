from datetime import datetime, timedelta
from typing import Dict, Any

from rest_framework import serializers

from weather_api.models import WeatherOverride


class CurrentWeatherQuerySerializer(serializers.Serializer):
    """
        Serializer for validating query parameters for current weather.
    """
    city = serializers.CharField(required=True)


class ForecastQuerySerializer(serializers.Serializer):
    """
        Serializer for validating query parameters for forecast weather.
    """
    city = serializers.CharField(required=True)
    date = serializers.DateField(input_formats=["%d.%m.%Y"], required=True)

    def validate_date(self, value: datetime.date) -> datetime.date:
        """
            Ensure the date is within the allowed forecast range.
        """
        today = datetime.today().date()
        if value < today:
            raise serializers.ValidationError("Date cannot be in the past")
        if value > today + timedelta(days=10):
            raise serializers.ValidationError("Date cannot be more than 10 days from today")
        return value


class ForecastOverrideSerializer(serializers.ModelSerializer):
    """
        Serializer for validating and saving forecast override data.
    """
    date = serializers.DateField(input_formats=["%d.%m.%Y"])

    class Meta:
        model = WeatherOverride
        fields = '__all__'
        validators = []   # disable default UniqueConstraint check

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        if data['min_temperature'] > data['max_temperature']:
            raise serializers.ValidationError("Min temperature cannot exceed max temperature")
        if data['date'] < datetime.today().date():
            raise serializers.ValidationError("Date cannot be in the past")
        if data['date'] > datetime.today().date() + timedelta(days=10):
            raise serializers.ValidationError("Date cannot be more than 10 days from today")
        return data
