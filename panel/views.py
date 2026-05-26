from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.urls import reverse
import threading
import sys
import os
from functools import wraps

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def mongo_login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.session.get('mongo_connected'):
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def login_view(request):
    if request.method == 'POST':
        mongo_user = request.POST.get('mongo_user')
        mongo_password = request.POST.get('mongo_password')
        mongo_host = request.POST.get('mongo_host', 'redes.x6zgvks.mongodb.net')
        
        try:
            from pymongo import MongoClient
            from config.settings import DATABASE_NAME
            
            mongo_uri = f"mongodb+srv://{mongo_user}:{mongo_password}@{mongo_host}/?appName=Redes"
            client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
            client.admin.command('ping')
            
            request.session['mongo_user'] = mongo_user
            request.session['mongo_password'] = mongo_password
            request.session['mongo_host'] = mongo_host
            request.session['mongo_connected'] = True
            
            return redirect('index')
        except Exception as e:
            return render(request, 'panel/login.html', {'error': f'Error de conexión: {str(e)}'})
    
    return render(request, 'panel/login.html')


def logout_view(request):
    request.session.flush()
    return redirect('login')

scan_progress = {
    'percentage': 0,
    'status': 'idle',
    'message': ''
}

_mongo_session_data = {}

def set_mongo_session_data(user, password, host):
    global _mongo_session_data
    _mongo_session_data = {
        'user': user,
        'password': password,
        'host': host
    }

def get_mongo_session_data():
    global _mongo_session_data
    return _mongo_session_data

def get_historial_repo():
    try:
        from repositories.historial_repository import historial_repository
        return historial_repository()
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        return None

def get_activos_repo():
    try:
        from repositories.activos_repository import activos_repository
        return activos_repository()
    except Exception as e:
        print(f"Error loading activos repository: {e}")
        return None

def get_logs_repo():
    try:
        from repositories.logs_repository import logs_repository
        return logs_repository()
    except Exception as e:
        print(f"Error loading logs repository: {e}")
        return None

def get_scanner_service():
    try:
        from services.scanner_service import scanner_service
        return scanner_service()
    except Exception as e:
        print(f"Error loading scanner service: {e}")
        return None

@mongo_login_required
def index(request):
    set_mongo_session_data(
        request.session.get('mongo_user'),
        request.session.get('mongo_password'),
        request.session.get('mongo_host')
    )
    
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

@mongo_login_required
@csrf_exempt
@require_POST
def scan(request):
    set_mongo_session_data(
        request.session.get('mongo_user'),
        request.session.get('mongo_password'),
        request.session.get('mongo_host')
    )
    
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

@mongo_login_required
def get_progress(request):
    global scan_progress
    return JsonResponse(scan_progress)

@mongo_login_required
def export_data(request):
    set_mongo_session_data(
        request.session.get('mongo_user'),
        request.session.get('mongo_password'),
        request.session.get('mongo_host')
    )
    
    datos = []
    repo = get_historial_repo()
    if repo:
        try:
            datos = repo.listar_todos_limpio()
        except Exception as e:
            print(f"Error exporting data: {e}")
    
    return JsonResponse({'datos': datos, 'count': len(datos)})


@mongo_login_required
def get_devices(request):
    set_mongo_session_data(
        request.session.get('mongo_user'),
        request.session.get('mongo_password'),
        request.session.get('mongo_host')
    )
    
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

@mongo_login_required
def get_activos(request):
    set_mongo_session_data(
        request.session.get('mongo_user'),
        request.session.get('mongo_password'),
        request.session.get('mongo_host')
    )
    
    repo = get_activos_repo()
    
    if repo:
        try:
            data = repo.listar_todos()
            for item in data:
                item["_id"] = str(item["_id"])
            
            return JsonResponse(data, safe=False)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'No se pudo obtener los activos'}, status=500)

@mongo_login_required
def get_dashboard(request):
    set_mongo_session_data(
        request.session.get('mongo_user'),
        request.session.get('mongo_password'),
        request.session.get('mongo_host')
    )
    
    repo = get_activos_repo()

    if repo:
        try:
            data = repo.obtener_dashboard()
            return JsonResponse(data, safe=False)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'No se pudo obtener el dashboard'}, status=500)

@mongo_login_required
def get_logs(request):
    set_mongo_session_data(
        request.session.get('mongo_user'),
        request.session.get('mongo_password'),
        request.session.get('mongo_host')
    )
    
    repo = get_logs_repo()

    if repo:
        try:
            data = repo.listar_todos()
            for item in data:
                item["_id"] = str(item["_id"])
                item["fecha"] = str(item["fecha"])
            
            return JsonResponse(data, safe=False)
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        
    return JsonResponse({'error': 'No se pudo cargar los logs'}, status=500)

@mongo_login_required
def query_page(request):
    set_mongo_session_data(
        request.session.get('mongo_user'),
        request.session.get('mongo_password'),
        request.session.get('mongo_host')
    )
    
    return render(
        request, "panel/query_builder.html"
    )


@mongo_login_required
def inventario_page(request):
    set_mongo_session_data(
        request.session.get('mongo_user'),
        request.session.get('mongo_password'),
        request.session.get('mongo_host')
    )
    
    repo = get_historial_repo()
    dispositivos = []
    
    if repo:
        try:
            todos = repo.listar_todos_limpio()
            macs_vistas = set()
            for item in todos:
                mac = item.get('mac')
                if mac and mac not in macs_vistas:
                    macs_vistas.add(mac)
                    dispositivos.append({
                        'mac': mac,
                        'nombre_dispositivo': item.get('nombre_dispositivo', item.get('host_name', '-'))
                    })
        except Exception as e:
            print(f"Error loading inventory: {e}")
    
    return render(request, 'panel/inventario.html', {'dispositivos': dispositivos})

@mongo_login_required
def query_campos(request):
    set_mongo_session_data(
        request.session.get('mongo_user'),
        request.session.get('mongo_password'),
        request.session.get('mongo_host')
    )
    
    try:
        from services.query_builder import query_builder_Service
        query = query_builder_Service()
        campos = query.obtener_campos_disponibles()
        return JsonResponse(campos, safe=False)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@mongo_login_required
@csrf_exempt
@require_POST
def ejecutar_query(request):
    set_mongo_session_data(
        request.session.get('mongo_user'),
        request.session.get('mongo_password'),
        request.session.get('mongo_host')
    )
    
    try:
        import json
        from services.query_builder_service import query_builder_service

        body = json.loads(request.body)

        query = query_builder_service()

        limite = int(body.get("limite", 100))

        orden_campo = body.get("orden")
        orden = {}

        if orden_campo:
            orden = {
                "campo": f"historial.{orden_campo}",
                "direccion": "desc"
            }

        filtros = []

        filtro = body.get("filtro")

        if filtro and filtro.get("campo") and filtro.get("valor"):
            filtros.append({
                "campo": f"historial.{filtro['campo']}",
                "operador": "contiene",
                "valor": filtro["valor"]
            })

        consulta = query.crear_consulta(
            coleccion_base="historial",
            campos=body["campos"],
            filtros=filtros,
            orden=orden,
            limite=limite
        )

        resultado = query.ejecutar_consulta(consulta)

        return JsonResponse(resultado, safe=False)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def get_export_service():
    try:
        from services.export_service import export_service
        return export_service()
    except Exception as e:
        print(f"Error loading export service: {e}")
        return None


@mongo_login_required
def export_csv(request):
    set_mongo_session_data(
        request.session.get('mongo_user'),
        request.session.get('mongo_password'),
        request.session.get('mongo_host')
    )
    
    from django.http import HttpResponse
    from datetime import datetime
    import csv
    
    repo = get_historial_repo()
    if not repo:
        return JsonResponse({'error': 'No se pudo conectar al repositorio'}, status=500)
    
    datos = repo.listar_todos_limpio()
    
    filename = f"historial_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    if datos:
        columnas = ['fecha', 'ip', 'mac', 'host_name', 'fabricante', 'estado', 'nombre_dispositivo']
        writer = csv.DictWriter(response, fieldnames=columnas, extrasaction='ignore')
        writer.writeheader()
        
        for item in datos:
            row = {col: item.get(col, '') for col in columnas}
            writer.writerow(row)
    
    return response


@mongo_login_required
def export_json(request):
    set_mongo_session_data(
        request.session.get('mongo_user'),
        request.session.get('mongo_password'),
        request.session.get('mongo_host')
    )
    
    from django.http import HttpResponse
    from datetime import datetime
    import json
    
    repo = get_historial_repo()
    if not repo:
        return JsonResponse({'error': 'No se pudo conectar al repositorio'}, status=500)
    
    datos = repo.listar_todos_limpio()
    
    filename = f"historial_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    response = HttpResponse(content_type='application/json')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    json.dump(datos, response, indent=4, ensure_ascii=False, default=str)
    
    return response


@mongo_login_required
def export_excel(request):
    set_mongo_session_data(
        request.session.get('mongo_user'),
        request.session.get('mongo_password'),
        request.session.get('mongo_host')
    )
    
    from django.http import HttpResponse
    from datetime import datetime
    import tempfile
    import os
    
    repo = get_historial_repo()
    if not repo:
        return JsonResponse({'error': 'No se pudo conectar al repositorio'}, status=500)
    
    datos = repo.listar_todos_limpio()
    
    export_svc = get_export_service()
    if not export_svc:
        return JsonResponse({'error': 'No se pudo inicializar el servicio de exportación'}, status=500)
    
    filename = f"historial_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
        tmp_path = tmp.name
    
    export_svc.exportar_excel(datos, tmp_path)
    
    with open(tmp_path, 'rb') as f:
        response = HttpResponse(
            f.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    os.unlink(tmp_path)
    
    return response

@mongo_login_required
def topologia_page(request):
    set_mongo_session_data(
        request.session.get('mongo_user'),
        request.session.get('mongo_password'),
        request.session.get('mongo_host')
    )   
    return render(request, "panel/topologia.html")

@mongo_login_required
def topologia_datos(request):
    set_mongo_session_data(
        request.session.get('mongo_user'),
        request.session.get('mongo_password'),
        request.session.get('mongo_host')
    )   
    try:
        from services.scanner_service import scanner_service
        from repositories.activos_repository import activos_repository
        scanner = scanner_service()
        scanner.escanar_y_guardar(
            tipo_escaneo="rapido"
        )
        repo = activos_repository()
        data = repo.listar_todos()
        for item in data:
            item["_id"] = str(item["_id"])
        return JsonResponse(data, safe=False)
    except Exception as e:
        import traceback
        traceback.print_exc()

        return JsonResponse(
            {
                "error": str(e)
            },
            status=500
        )
