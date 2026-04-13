from django.urls import path
from . import views

app_name = 'expenses'

urlpatterns = [
    path('add/', views.add_expense, name='add'),
    path('toggle-no-expense/', views.toggle_no_expense, name='toggle_no_expense'),
    path('<int:expense_id>/edit/', views.edit_expense, name='edit'),
    path('<int:expense_id>/delete/', views.delete_expense, name='delete'),
]
