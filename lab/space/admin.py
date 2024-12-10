# admin.py
from django.contrib import admin
from .models import SpaceStation, Satellite, Astronaut

class SatelliteInline(admin.TabularInline):
    model = Satellite
    extra = 1

class AstronautInline(admin.TabularInline):
    model = Astronaut
    extra = 1

@admin.register(SpaceStation)
class SpaceStationAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'launch_year', 'country')
    search_fields = ('name', 'country')
    list_filter = ('country','name')
    inlines = [SatelliteInline, AstronautInline]

@admin.register(Satellite)
class SatelliteAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'station', 'orbit_type')
    list_filter = ('orbit_type','name')

@admin.register(Astronaut)
class AstronautAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'station', 'missions_count')
    list_filter = ('missions_count','name')