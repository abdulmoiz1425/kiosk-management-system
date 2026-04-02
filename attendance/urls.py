from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    path('checkin/', views.checkin, name='checkin'),
    path('checkout/', views.checkout, name='checkout'),
]
