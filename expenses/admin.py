from django.contrib import admin
from .models import Expense, NoExpenseDay


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('kiosk', 'date', 'category', 'amount', 'description', 'recorded_by')
    list_filter = ('kiosk', 'category', 'date')
    search_fields = ('kiosk__name', 'description', 'recorded_by__username')
    date_hierarchy = 'date'


@admin.register(NoExpenseDay)
class NoExpenseDayAdmin(admin.ModelAdmin):
    list_display = ('kiosk', 'date', 'recorded_by', 'created_at')
    list_filter = ('kiosk', 'date')
    search_fields = ('kiosk__name', 'recorded_by__username')
    date_hierarchy = 'date'
