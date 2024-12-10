from django.shortcuts import render, get_object_or_404, redirect
from .models import SpaceStation, Satellite, Astronaut
from .forms import SpaceStationForm, SatelliteForm, AstronautForm

def index(request):
    space_stations = SpaceStation.objects.all()
    satellites = Satellite.objects.all()
    astronauts = Astronaut.objects.all()
    return render(request, 'index.html', {
        'space_stations': space_stations,
        'satellites': satellites,
        'astronauts': astronauts
    })

def add_space_station(request):
    if request.method == 'POST':
        form = SpaceStationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = SpaceStationForm()
    return render(request, 'add_space_station.html', {'form': form})

def add_satellite(request):
    if request.method == 'POST':
        form = SatelliteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = SatelliteForm()
    return render(request, 'add_satellite.html', {'form': form})

def add_astronaut(request):
    if request.method == 'POST':
        form = AstronautForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = AstronautForm()
    return render(request, 'add_astronaut.html', {'form': form})

def space_station_detail(request, pk):
    station = get_object_or_404(SpaceStation, pk=pk)
    return render(request, 'space_station_detail.html', {'station': station})

def satellite_detail(request, pk):
    satellite = get_object_or_404(Satellite, pk=pk)
    return render(request, 'satellite_detail.html', {'satellite': satellite})

def astronaut_detail(request, pk):
    astronaut = get_object_or_404(Astronaut, pk=pk)
    return render(request, 'astronaut_detail.html', {'astronaut': astronaut})

def edit_space_station(request, pk):
    station = get_object_or_404(SpaceStation, pk=pk)
    if request.method == 'POST':
        form = SpaceStationForm(request.POST, instance=station)
        if form.is_valid():
            form.save()
            return redirect('space_station_detail', pk=station.pk)
    else:
        form = SpaceStationForm(instance=station)
    return render(request, 'edit_space_station.html', {'form': form})

def edit_satellite(request, pk):
    satellite = get_object_or_404(Satellite, pk=pk)
    if request.method == 'POST':
        form = SatelliteForm(request.POST, instance=satellite)
        if form.is_valid():
            form.save()
            return redirect('satellite_detail', pk=satellite.pk)
    else:
        form = SatelliteForm(instance=satellite)
    return render(request, 'edit_satellite.html', {'form': form})

def edit_astronaut(request, pk):
    astronaut = get_object_or_404(Astronaut, pk=pk)
    if request.method == 'POST':
        form = AstronautForm(request.POST, instance=astronaut)
        if form.is_valid():
            form.save()
            return redirect('astronaut_detail', pk=astronaut.pk)
    else:
        form = AstronautForm(instance=astronaut)
    return render(request, 'edit_astronaut.html', {'form': form})
