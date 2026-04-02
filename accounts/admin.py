from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'kiosk', 'is_active')
    list_filter = ('role', 'is_active', 'kiosk')
    fieldsets = UserAdmin.fieldsets + (
        ('Role & Kiosk', {'fields': ('role', 'phone', 'profile_photo', 'kiosk')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Role & Kiosk', {'fields': ('role', 'phone', 'kiosk')}),
    )
