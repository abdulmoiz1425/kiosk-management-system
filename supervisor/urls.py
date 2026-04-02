from django.urls import path
from . import views

app_name = 'supervisor'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('visits/', views.visits_list, name='visits'),
    path('visits/log/', views.log_visit, name='log_visit'),
    path('bonus-penalty/', views.add_bonus_penalty, name='bonus_penalty'),
    path('performance/', views.employee_performance, name='performance'),
    path('employee/<int:user_id>/', views.employee_detail, name='employee_detail'),
]
