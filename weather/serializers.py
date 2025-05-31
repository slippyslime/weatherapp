from rest_framework import serializers
from .models import City, SearchHistory


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = '__all__'


class SearchHistorySerializer(serializers.ModelSerializer):
    city = CitySerializer()

    class Meta:
        model = SearchHistory
        fields = '__all__'