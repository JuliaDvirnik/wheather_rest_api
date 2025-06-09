from django.contrib import admin

from weather_api.models import WeatherOverride


# Register your models here.
@admin.register(WeatherOverride)
class WeatherOverrideAdmin(admin.ModelAdmin):
    list_display = ("city", "date", "min_temperature", "max_temperature")
    list_filter = ("city", "date")
    search_fields = ("city",)