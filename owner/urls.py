from django.urls import path
from . import views

app_name = 'owner'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('attendance/', views.attendance_overview, name='attendance'),
    path('visits/', views.supervisor_visits, name='visits'),
    path('reports/', views.monthly_report, name='reports'),
    path('kiosk/<int:kiosk_id>/', views.kiosk_detail, name='kiosk_detail'),
]
