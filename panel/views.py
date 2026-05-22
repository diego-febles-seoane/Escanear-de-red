from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import threading
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

scan_progress = {
    'percentage': 0,
    'status': 'idle',
    'message': ''
}

def get_historial_repo():
    try:
        from repositories.historial_repository import historial_repository
        return historial_repository()
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        return None

def get_scanner_service():
    try:
        from services.scanner_service import scanner_service
        return scanner_service()
    except Exception as e:
        print(f"Error loading scanner service: {e}")
        return None

def index(request):
    historial = []
    repo = get_historial_repo()
    if repo:
        try:
            historial = repo.listar_todos_limpio()
        except Exception as e:
            print(f"Error loading historial: {e}")
    
    return render(request, 'panel/escaner.html', {
        'historial': historial,
        'progress': scan_progress
    })

@csrf_exempt
@require_POST
def scan(request):
    global scan_progress
    
    if scan_progress['status'] == 'running':
        return JsonResponse({'status': 'already_running'})
    
    scan_progress = {
        'percentage': 0,
        'status': 'running',
        'message': 'Iniciando escaneo...'
    }
    
    def run_scan():
        global scan_progress
        try:
            scanner = get_scanner_service()
            if not scanner:
                raise Exception("No se pudo inicializar el servicio de escaneo")
            
            scan_progress['percentage'] = 10
            scan_progress['message'] = 'Escaneando red...'
            
            ids = scanner.escanar_y_guardar()
            
            scan_progress['percentage'] = 100
            scan_progress['status'] = 'finished'
            scan_progress['message'] = 'Escaneo completado'
        except Exception as e:
            scan_progress['status'] = 'error'
            scan_progress['message'] = f'Error: {str(e)}'
            print(f"Scan error: {e}")
    
    thread = threading.Thread(target=run_scan)
    thread.daemon = True
    thread.start()
    
    return JsonResponse({'status': 'started'})

def get_progress(request):
    global scan_progress
    return JsonResponse(scan_progress)

def export_data(request):
    datos = []
    repo = get_historial_repo()
    if repo:
        try:
            datos = repo.listar_todos_limpio()
        except Exception as e:
            print(f"Error exporting data: {e}")
    
    return JsonResponse({'datos': datos, 'count': len(datos)})


def get_devices(request):
    
    repo = get_historial_repo()
    
    if repo:
        try:
    
            data = repo.listar_todos_limpio()
            
    
            print(f"\n[CMD] Enviando {len(data)} dispositivos a la vista JSON\n")
            
            return JsonResponse(data, safe=False)
        except Exception as e:
            print(f"Error al obtener dispositivos: {e}")
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'No se pudo conectar al repositorio'}, status=500)