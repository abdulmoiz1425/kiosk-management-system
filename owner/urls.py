from django.urls import path
from . import views

app_name = 'owner'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    # Kiosk CRUD
    path('kiosks/', views.kiosks_list, name='kiosks_list'),
    path('kiosks/create/', views.create_kiosk, name='create_kiosk'),
    path('kiosk/<int:kiosk_id>/', views.kiosk_detail, name='kiosk_detail'),
    path('kiosk/<int:kiosk_id>/edit/', views.edit_kiosk, name='edit_kiosk'),
    path('kiosk/<int:kiosk_id>/delete/', views.delete_kiosk, name='delete_kiosk'),
    # Employee CRUD
    path('employees/', views.employees_list, name='employees_list'),
    path('employees/create/', views.create_employee, name='create_employee'),
    path('employees/<int:user_id>/edit/', views.edit_employee, name='edit_employee'),
    path('employees/<int:user_id>/delete/', views.delete_employee, name='delete_employee'),
    # Other views
    path('attendance/', views.attendance_overview, name='attendance'),
    path('visits/', views.supervisor_visits, name='visits'),
    path('reports/', views.monthly_report, name='reports'),
]
