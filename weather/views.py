from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import City, SearchHistory
from .serializers import CitySerializer, SearchHistorySerializer
import requests
from django.utils import timezone
from urllib.parse import quote, unquote


def home(request):
    last_city = unquote(request.COOKIES.get('last_city', ''))
    history = SearchHistory.objects.order_by('-last_searched')[:10]
    return render(request, 'weather/index.html', {
        'last_city': last_city,
        'history': history
    })


@api_view(['GET'])
def weather_api(request, city_name):
    # 1 Получение координат города
    geo_url = 'https://nominatim.openstreetmap.org/search'
    params = {
        'q': city_name,
        'format': 'json',
        'limit': 1,
    }

    geo_response = requests.get(geo_url, params=params, headers={'User-Agent': 'WeatherApp/1.0', 'Accept-Language': 'ru,en;q=0.9'})
    geo_data = geo_response.json()

    if not geo_data:
        return Response({'error': 'City is not finded'}, status=404)

    lat = float(geo_data[0]['lat'])
    lon = float(geo_data[0]['lon'])
    country = geo_data[0].get('display_name', '').split(',')[-1].strip()

    # 2 Ищем или создаем город
    city, created = City.objects.get_or_create(
        name=city_name,
        defaults={'latitude': lat, 'longitude': lon, 'country': country}
    )

    # 3 Обновляем историю поиска
    history, _ = SearchHistory.objects.get_or_create(city=city)
    history.search_count += 1
    history.last_searched = timezone.now()
    history.save()

    # 4 Получаем погоду
    weather_data = get_weather(lat, lon)

    response = Response({
        'city': CitySerializer(city).data,
        'weather': weather_data
    })

    # 5 Кука с последним городом
    response.set_cookie('last_city', quote(city_name))

    return response

@api_view(['GET'])
def city_search(request):
    query = request.GET.get('q', '').strip()
    if not query:
        return Response([])

    url = 'https://nominatim.openstreetmap.org/search'
    params = {
        'q': query,
        'format': 'json',
        'addressdetails': 1,
        'limit': 5,
    }

    try:
        response = requests.get(url, params=params, headers={'User-Agent': 'WeatherApp/1.0', 'Accept-Language': 'ru,en;q=0.9'}, timeout=3)
        data = response.json()
    except Exception as e:
        return Response({'error': 'Error geosearch'}, status=500)

    results = []
    for item in data:
        address = item.get('address', {})
        city = address.get('city') or address.get('town') or address.get('village') or address.get('hamlet')
        country = address.get('country')
        if city and country:
            results.append({'name': city, 'country': country})

    return Response(results)


@api_view(['GET'])
def search_history(request):
    history = SearchHistory.objects.order_by('-last_searched')[:10]
    serializer = SearchHistorySerializer(history, many=True)
    return Response(serializer.data)


def get_weather(latitude, longitude):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current_weather": True,
        "hourly": "temperature_2m,relativehumidity_2m,windspeed_10m"
    }
    response = requests.get(url, params=params)
    return response.json()