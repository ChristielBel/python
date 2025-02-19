# forms.py
from django import forms
from .models import SpaceStation, Satellite, Astronaut

class SpaceStationForm(forms.ModelForm):
    class Meta:
        model = SpaceStation
        fields = ['name', 'launch_year', 'country']

class SatelliteForm(forms.ModelForm):
    class Meta:
        model = Satellite
        fields = ['name', 'station', 'orbit_type']

class AstronautForm(forms.ModelForm):
    class Meta:
        model = Astronaut
        fields = ['name', 'station', 'missions_count']
