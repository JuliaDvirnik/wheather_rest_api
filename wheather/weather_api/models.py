from django.db import models


class WeatherOverride(models.Model):
    city = models.CharField(max_length=100)
    date = models.DateField()
    min_temperature = models.FloatField()
    max_temperature = models.FloatField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['city', 'date'], name='unique_city_date')
        ]