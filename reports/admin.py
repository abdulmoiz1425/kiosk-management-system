from django.contrib import admin
from .models import DailyReport, ReportPhoto


class ReportPhotoInline(admin.TabularInline):
    model = ReportPhoto
    extra = 0


@admin.register(DailyReport)
class DailyReportAdmin(admin.ModelAdmin):
    list_display = ('kiosk', 'date', 'submitted_by', 'submitted_at')
    list_filter = ('kiosk', 'date')
    search_fields = ('kiosk__name', 'submitted_by__username')
    date_hierarchy = 'date'
    inlines = [ReportPhotoInline]


@admin.register(ReportPhoto)
class ReportPhotoAdmin(admin.ModelAdmin):
    list_display = ('report', 'uploaded_at')
    list_filter = ('report__kiosk',)
