from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('api/weather/<str:city_name>/', views.weather_api, name='weather_api'),
    path('api/city-search/', views.city_search, name='city_search'),
    path('api/history/', views.search_history, name='search_history'),
]