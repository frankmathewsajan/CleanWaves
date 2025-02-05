from django.db import models


class SensorData(models.Model):
    temp = models.FloatField()
    lat = models.FloatField()
    lon = models.FloatField()
    alt = models.FloatField()
    heading = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)  # Automatically set the time when created

    def __str__(self):
        return f"SensorData at {self.timestamp}"
