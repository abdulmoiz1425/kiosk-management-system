from django.contrib import admin
from .models import Kiosk


@admin.register(Kiosk)
class KioskAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'location')
