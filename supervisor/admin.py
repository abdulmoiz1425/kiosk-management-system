from django.contrib import admin
from .models import SupervisorVisit, BonusPenalty


@admin.register(SupervisorVisit)
class SupervisorVisitAdmin(admin.ModelAdmin):
    list_display = ('supervisor', 'kiosk', 'date', 'rating')
    list_filter = ('kiosk', 'rating', 'date')


@admin.register(BonusPenalty)
class BonusPenaltyAdmin(admin.ModelAdmin):
    list_display = ('employee', 'type', 'amount', 'issued_by', 'date')
    list_filter = ('type', 'date')
