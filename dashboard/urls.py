from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.home, name='home'),
    path('owner/', views.owner_dashboard, name='owner'),
    path('supervisor/', views.supervisor_dashboard, name='supervisor'),
    path('employee/', views.employee_dashboard, name='employee'),
    path('employee/history/', views.employee_history, name='history'),
]
