"""
URL configuration for lab project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from space import views

urlpatterns = [
    path('', views.index, name='index'),
    path('admin/', admin.site.urls),
    path('space_station/add/', views.add_space_station, name='add_space_station'),
    path('space_station/<int:pk>/', views.space_station_detail, name='space_station_detail'),
    path('satellite/add/', views.add_satellite, name='add_satellite'),
    path('satellite/<int:pk>/', views.satellite_detail, name='satellite_detail'),
    path('astronaut/add/', views.add_astronaut, name='add_astronaut'),
    path('astronaut/<int:pk>/', views.astronaut_detail, name='astronaut_detail'),
    path('edit_space_station/<int:pk>/', views.edit_space_station, name='edit_space_station'),
    path('edit_satellite/<int:pk>/', views.edit_satellite, name='edit_satellite'),
    path('edit_astronaut/<int:pk>/', views.edit_astronaut, name='edit_astronaut'),
]