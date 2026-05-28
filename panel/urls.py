from django.urls import path
from . import views

urlpatterns = [

    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.index, name='index'),
    path('inventario/', views.inventario_page, name='inventario'),
    path('scan/', views.scan, name='scan'),
    path(
        'get-devices/',
        views.get_devices,
        name='get_devices'
    ),
    path(
        'progress/',
        views.get_progress,
        name='get_progress'
    ),

    path(
        'get-activos/',
        views.get_activos,
        name='get_activos'
    ),
    path(
        'dashboard/',
        views.get_dashboard,
        name='dashboard'
    ),
    path(
        'logs/',
        views.get_logs,
        name='logs'
    ),
    path(
        'query/',
        views.query_page,
        name='query'
    ),
    path(
        'query-campos/',
        views.query_campos,
        name='query_campos'
    ),
    path(
        'ejecutar-query/',
        views.ejecutar_query,
        name='ejecutar_query'
    ),
    
    path('export/csv/', views.export_csv, name='export_csv'),
    path('export/json/', views.export_json, name='export_json'),
    path('export/excel/', views.export_excel, name='export_excel'),
    path('export/pdf/', views.export_pdf, name='export_pdf'),
    path('topologia/', views.topologia_page, name='topologia'),
    path('topologia-datos/', views.topologia_datos, name='topologia_datos'),
    path('alertas/', views.alerts_page, name='alertas'),
    path('get-stats/', views.get_stats, name='get_stats'),
    
 ]