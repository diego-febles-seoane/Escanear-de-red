from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('scan/', views.scan, name='scan'),
    path('progress/', views.get_progress, name='get_progress'),
    path('export/', views.export_data, name='export_data'),
    path('devices/', views.get_devices, name='get_devices'),
]
