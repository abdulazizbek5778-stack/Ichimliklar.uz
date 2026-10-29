from django.contrib import admin
from .models import WaterProduct

@admin.register(WaterProduct)
class WaterProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'water_type', 'volume', 'price', 'stock', 'origin', 'is_active')
    list_filter = ('water_type', 'is_active', 'origin')
    search_fields = ('name', 'origin', 'description')
    list_editable = ('price', 'stock', 'is_active')
