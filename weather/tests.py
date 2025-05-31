from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import City, SearchHistory
from unittest.mock import patch

# Вспомогательный класс для моков
class MockResponse:
    def __init__(self, json_data, status_code):
        self._json_data = json_data
        self.status_code = status_code

    def json(self):
        return self._json_data

    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception(f"HTTP error: {self.status_code}")

class WeatherAPITests(APITestCase):

    @patch('weather.views.requests.get')
    def test_weather_api_success(self, mock_get):
        # Мокаем ответ от nominatim
        mock_get.side_effect = [
            # Геоданные от nominatim
            MockResponse([{
                'lat': '55.7558',
                'lon': '37.6173',
                'display_name': 'Moscow, Russia'
            }], 200),
            # Погодные данные
            MockResponse({
                'current_weather': {'temperature': 15, 'windspeed': 3}
            }, 200)
        ]

        url = reverse('weather_api', args=['Moscow'])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('city', response.data)
        self.assertIn('weather', response.data)
        self.assertTrue(City.objects.filter(name='Moscow').exists())
        self.assertTrue(SearchHistory.objects.filter(city__name='Moscow').exists())

    @patch('weather.views.requests.get')
    def test_weather_api_city_not_found(self, mock_get):
        mock_get.return_value = MockResponse([], 200)

        url = reverse('weather_api', args=['FakeCity'])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)

    def test_search_history_endpoint(self):
        city = City.objects.create(name='Paris', latitude=48.8566, longitude=2.3522, country='France')
        SearchHistory.objects.create(city=city, search_count=3)

        url = reverse('search_history')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertGreaterEqual(len(response.data), 1)

    @patch('weather.views.requests.get')
    def test_city_search(self, mock_get):
        mock_get.return_value = MockResponse([
            {
                'address': {'city': 'Berlin', 'country': 'Germany'}
            }
        ], 200)

        url = reverse('city_search') + '?q=Berlin'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Berlin')
