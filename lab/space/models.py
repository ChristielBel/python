# models.py
from django.db import models

class SpaceStation(models.Model):
    name = models.CharField(max_length=255)
    launch_year = models.IntegerField()
    country = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Satellite(models.Model):
    name = models.CharField(max_length=255)
    station = models.ForeignKey(SpaceStation, on_delete=models.CASCADE, related_name="satellites")
    orbit_type = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Astronaut(models.Model):
    name = models.CharField(max_length=255)
    station = models.ForeignKey(SpaceStation, on_delete=models.CASCADE, related_name="astronauts")
    missions_count = models.IntegerField()

    def __str__(self):
        return self.name
