from django.contrib import admin
from .models import City, SearchHistory


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'latitude', 'longitude')
    search_fields = ('name', 'country')


@admin.register(SearchHistory)
class SearchHistoryAdmin(admin.ModelAdmin):
    list_display = ('city', 'search_count', 'get_last_searched')
    list_filter = ('city',)

    def get_last_searched(self, obj):
        return obj.last_searched

    get_last_searched.short_description = 'Last Searched'
    get_last_searched.admin_order_field = 'last_searched'