from django.urls import path
from . import views

app_name = 'sales'

urlpatterns = [
    path('add/', views.add_sale, name='add'),
]
