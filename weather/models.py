from email.policy import default

from django.db import models
from django.utils import timezone


class City(models.Model):
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=100, blank=True, null=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}, {self.country}" if self.country else self.name


class SearchHistory(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    search_count = models.PositiveIntegerField(default=1)
    last_searched = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Search Histories"
        ordering = ['-last_searched']

    def __str__(self):
        return f"{self.city.name} (searched {self.search_count} times)"