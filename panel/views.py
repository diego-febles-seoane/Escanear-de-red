from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.template.loader import render_to_string
from xhtml2pdf import pisa
import io
import threading
from datetime import datetime, timedelta
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

def get_alertas_repo():
    try:
        from repositories.alertas_repository import alertas_repository
        return alertas_repository()
    except Exception as e:
        print(f"Error loading alertas repository: {e}")
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
        'message': 'Iniciando observación pasiva...'
    }
    
    def run_scan(m_user, m_pass, m_host):
        global scan_progress
        try:
            # Restaurar contexto de MongoDB en el nuevo hilo
            set_mongo_session_data(m_user, m_pass, m_host)
            
            scanner = get_scanner_service()
            if not scanner:
                raise Exception("No se pudo inicializar el servicio de escaneo")
            
            def progress_callback(percentage, message):
                scan_progress['percentage'] = percentage
                scan_progress['message'] = message

            # Realizar observación pasiva sin enviar paquetes
            ids = scanner.escanar_y_guardar(progress_callback=progress_callback)
            
            scan_progress['percentage'] = 100
            scan_progress['status'] = 'finished'
            if ids:
                scan_progress['message'] = 'Observación completada con éxito'
            else:
                scan_progress['message'] = 'Finalizado. No se detectó actividad reciente.'
                
        except Exception as e:
            scan_progress['status'] = 'error'
            scan_progress['message'] = f'Error: {str(e)}'
            print(f"Scan error: {e}")
    
    m_user = request.session.get('mongo_user')
    m_pass = request.session.get('mongo_password')
    m_host = request.session.get('mongo_host')
    
    thread = threading.Thread(target=run_scan, args=(m_user, m_pass, m_host))
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

def get_last_active_devices():
    repo_historial = get_historial_repo()
    if not repo_historial:
        return []
    
    # Obtenemos los últimos registros únicos por MAC del historial
    pipeline = [
        {"$sort": {"fecha": -1}},
        {
            "$group": {
                "_id": "$mac",
                "latest": {"$first": "$$ROOT"}
            }
        },
        {"$replaceRoot": {"newRoot": "$latest"}}
    ]
    
    data = list(repo_historial.collection.aggregate(pipeline))
    
    for item in data:
        item["_id"] = str(item["_id"])
        if "tipo_dispositivo" not in item and "tipo" in item:
            item["tipo_dispositivo"] = item["tipo"]
            
    return data

@mongo_login_required
def get_activos(request):
    set_mongo_session_data(
        request.session.get('mongo_user'),
        request.session.get('mongo_password'),
        request.session.get('mongo_host')
    )
    
    try:
        repo = get_activos_repo()
        if not repo:
            return JsonResponse({'error': 'No se pudo conectar al repositorio de activos'}, status=500)
        
        # Obtenemos directamente de la colección 'activos' que se borra y rellena en cada escaneo
        data = list(repo.collection.find())
        
        for item in data:
            item["_id"] = str(item["_id"])
            if "tipo_dispositivo" not in item and "tipo" in item:
                item["tipo_dispositivo"] = item["tipo"]
                
        print(f"Enviando {len(data)} dispositivos del último escaneo a la topología")
        return JsonResponse(data, safe=False)
    except Exception as e:
        print(f"Error al obtener activos: {e}")
        return JsonResponse({'error': str(e)}, status=500)

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
        from services.query_builder import query_builder_Service

        body = json.loads(request.body)

        query = query_builder_Service()

        limite = int(body.get("limite", 100))

        orden_campo = body.get("orden")
        orden = {}

        if orden_campo:
            # Si el campo ya tiene el prefijo de la colección (p.ej. "historial.ip"), lo usamos tal cual
            if "." not in orden_campo:
                orden_campo = f"historial.{orden_campo}"
            
            orden = {
                "campo": orden_campo,
                "direccion": "desc"
            }

        filtros = []

        filtro = body.get("filtro")

        if filtro and filtro.get("campo") and filtro.get("valor"):
            filtro_campo = filtro['campo']
            if "." not in filtro_campo:
                filtro_campo = f"historial.{filtro_campo}"

            filtros.append({
                "campo": filtro_campo,
                "operador": "contiene",
                "valor": filtro["valor"]
            })

        fecha_desde = body.get("fecha_desde")
        fecha_hasta = body.get("fecha_hasta")

        if fecha_desde and fecha_hasta:
            filtros.append({
                "campo": "historial.fecha",
                "operador": "entre",
                "valor": {
                    "desde": fecha_desde,
                    "hasta": fecha_hasta
                }
            })
        elif fecha_desde:
            filtros.append({
                "campo": "historial.fecha",
                "operador": "mayor_que",
                "valor": fecha_desde
            })
        elif fecha_hasta:
            filtros.append({
                "campo": "historial.fecha",
                "operador": "menor_que",
                "valor": fecha_hasta
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


@mongo_login_required
def get_stats(request):
    set_mongo_session_data(
        request.session.get('mongo_user'),
        request.session.get('mongo_password'),
        request.session.get('mongo_host')
    )
    
    repo_historial = get_historial_repo()
    
    # 1. Escaneos últimos 3 días (agrupados por día)
    stats_escaneos = []
    hoy = datetime.now()
    for i in range(2, -1, -1):
        dia = hoy - timedelta(days=i)
        inicio_dia = dia.replace(hour=0, minute=0, second=0, microsecond=0)
        fin_dia = dia.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        # Contar registros en ese día
        count = repo_historial.collection.count_documents({
            "fecha": {"$gte": inicio_dia, "$lte": fin_dia}
        })
        stats_escaneos.append({
            "dia": dia.strftime("%d/%m"),
            "cantidad": count
        })
    
    # 2. Niveles de riesgo (último estado de cada dispositivo)
    repo_activos = get_activos_repo()
    activos = repo_activos.listar_todos()
    stats_riesgo = {"ALTO": 0, "MEDIO": 0, "BAJO": 0}
    
    for a in activos:
        riesgo = str(a.get("riesgo", "BAJO")).upper()
        if riesgo in stats_riesgo:
            stats_riesgo[riesgo] += 1
            
    return JsonResponse({
        "escaneos": stats_escaneos,
        "riesgo": [
            {"nivel": "ALTO", "cantidad": stats_riesgo["ALTO"]},
            {"nivel": "MEDIO", "cantidad": stats_riesgo["MEDIO"]},
            {"nivel": "BAJO", "cantidad": stats_riesgo["BAJO"]}
        ]
    })


@mongo_login_required
def alerts_page(request):
    set_mongo_session_data(
        request.session.get('mongo_user'),
        request.session.get('mongo_password'),
        request.session.get('mongo_host')
    )
    
    repo = get_alertas_repo()
    if not repo:
        return render(request, "panel/alertas.html", {"alertas": [], "error": "No se pudo conectar al repositorio de alertas"})

    alertas = repo.listar_todas()
    
    # Limpiar IDs y fechas para JSON/Template
    for a in alertas:
        a["_id"] = str(a["_id"])
        if "fecha" in a:
            a["fecha"] = a["fecha"].strftime("%Y-%m-%d %H:%M:%S")
            
    return render(request, "panel/alertas.html", {"alertas": alertas})


def get_export_service():
    try:
        from services.export_service import export_service
        return export_service()
    except Exception as e:
        print(f"Error loading export service: {e}")
        return None


@mongo_login_required
def export_pdf(request):
    set_mongo_session_data(
        request.session.get('mongo_user'),
        request.session.get('mongo_password'),
        request.session.get('mongo_host')
    )
    
    repo = get_historial_repo()
    if not repo:
        return HttpResponse("Error: No se pudo conectar a la base de datos", status=500)
    
    try:
        dispositivos = repo.listar_todos_limpio()
        
        # Calcular algunas estadísticas para el resumen
        total = len(dispositivos)
        riesgo_alto = sum(1 for d in dispositivos if str(d.get('riesgo', '')).upper() == 'ALTO')
        
        context = {
            'dispositivos': dispositivos,
            'total_dispositivos': total,
            'riesgo_alto': riesgo_alto,
            'fecha_actual': datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        }
        
        # Renderizar el HTML
        html_string = render_to_string('panel/reporte_pdf.html', context)
        
        # Crear el PDF
        result = io.BytesIO()
        pdf = pisa.pisaDocument(io.BytesIO(html_string.encode("UTF-8")), result)
        
        if not pdf.err:
            response = HttpResponse(result.getvalue(), content_type='application/pdf')
            filename = f"Informe_Red_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
            
        return HttpResponse("Error al generar el PDF", status=500)
        
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return HttpResponse(f"Error: {str(e)}", status=500)


@mongo_login_required
def export_pdf_documentacion(request):
    try:
        context = {
            'fecha_actual': datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        }
        
        # Renderizar el HTML de la documentación
        html_string = render_to_string('panel/reporte_documentacion_pdf.html', context)
        
        # Crear el PDF
        result = io.BytesIO()
        pdf = pisa.pisaDocument(io.BytesIO(html_string.encode("UTF-8")), result)
        
        if not pdf.err:
            response = HttpResponse(result.getvalue(), content_type='application/pdf')
            filename = f"Documentacion_Proyecto_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
            
        return HttpResponse("Error al generar el PDF de documentación", status=500)
        
    except Exception as e:
        print(f"Error generating documentation PDF: {e}")
        return HttpResponse(f"Error: {str(e)}", status=500)


@mongo_login_required
def export_csv(request):
    set_mongo_session_data(
        request.session.get('mongo_user'),
        request.session.get('mongo_password'),
        request.session.get('mongo_host')
    )
    
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
    
    import tempfile
    
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
    
    global scan_progress
    
    # Si ya hay un escaneo en curso, no iniciamos otro pero devolvemos los datos actuales
    if scan_progress['status'] == 'running':
        repo_activos = get_activos_repo()
        data = repo_activos.listar_todos_limpio() if repo_activos else []
        return JsonResponse({"status": "running", "data": data})

    try:
        # Iniciamos la observación pasiva de forma asíncrona para no bloquear
        scan_progress = {
            'percentage': 0,
            'status': 'running',
            'message': 'Iniciando observación pasiva para topología...'
        }

        def run_topo_scan(m_user, m_pass, m_host):
            global scan_progress
            try:
                # Restaurar contexto de MongoDB en el nuevo hilo
                set_mongo_session_data(m_user, m_pass, m_host)
                
                scanner = get_scanner_service()
                if scanner:
                    scan_progress['percentage'] = 10
                    scan_progress['message'] = 'Observando red (Topología)...'
                    scanner.escanar_y_guardar()
                
                scan_progress['percentage'] = 100
                scan_progress['status'] = 'finished'
                scan_progress['message'] = 'Observación de topología completada'
            except Exception as e:
                scan_progress['status'] = 'error'
                scan_progress['message'] = str(e)
                print(f"Topo scan error: {e}")

        m_user = request.session.get('mongo_user')
        m_pass = request.session.get('mongo_password')
        m_host = request.session.get('mongo_host')
        
        thread = threading.Thread(target=run_topo_scan, args=(m_user, m_pass, m_host))
        thread.daemon = True
        thread.start()

        repo_activos = get_activos_repo()
        data = repo_activos.listar_todos_limpio() if repo_activos else []
            
        return JsonResponse({"status": "started", "data": data})
    except Exception as e:
        print(f"Error en topologia_datos: {e}")
        return JsonResponse({"error": str(e)}, status=500)
