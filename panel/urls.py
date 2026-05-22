from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('scan/', views.scan, name='scan'),
    path('get-devices/', views.get_devices, name='get_devices'),
    path('progress/', views.get_progress, name='get_progress'),
]