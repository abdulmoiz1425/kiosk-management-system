from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('dashboard/', include('dashboard.urls', namespace='dashboard')),
    path('attendance/', include('attendance.urls', namespace='attendance')),
    path('sales/', include('sales.urls', namespace='sales')),
    path('expenses/', include('expenses.urls', namespace='expenses')),
    path('reports/', include('reports.urls', namespace='reports')),
    path('supervisor/', include('supervisor.urls', namespace='supervisor')),
    path('owner/', include('owner.urls', namespace='owner')),
    path('', lambda request: redirect('dashboard:home'), name='root'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
