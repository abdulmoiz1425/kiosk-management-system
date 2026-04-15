from django.contrib import admin
from .models import Sale


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('kiosk', 'date', 'starting_cash', 'cash_amount', 'bank_transfer_amount', 'actual_cash', 'recorded_by')
    list_filter = ('kiosk', 'date')
    search_fields = ('kiosk__name', 'recorded_by__username')
    date_hierarchy = 'date'
