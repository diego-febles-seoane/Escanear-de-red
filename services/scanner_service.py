from managers.network_manager import network_manager
from models.historial import Historial
from repositories.historial_repository import historial_repository
from services.vendor_service import vendor_service
from services.device_classifier_service import device_classifier_service
from repositories.activos_repository import activos_repository
from repositories.logs_repository import logs_repository
from services.alertas_service import alertas_service
from services.risk_service import risk_service
from services.comparador_service import comparador_service

"""
Servicio de escaneo de red para obtener información de los dispositivos
"""
class scanner_service:
    """
    Servicio de escaneo de red para obtener información de los dispositivo en la red
    y guardarlos en la base de datos Historial
    """
    def __init__(self):
        self.network = network_manager()
        self.repo = historial_repository()
        self.vendor = vendor_service()
        self.classifier = device_classifier_service()
        self.activos_repo = activos_repository()
        self.logs_repo = logs_repository()
        self.alertas = alertas_service()
        self.risk = risk_service()
        self.comparador = comparador_service()

    """
    Obtiene la ubicación de un dispositivo en base a su fabricante, tipo y IP
    @param ip: IP del dispositivo
    @param fabricante: Fabricante del dispositivo
    @param tipo: Tipo del dispositivo
    @param gateway_ip: IP del gateway
    @return: Ubicación del dispositivo
    """
    def obtener_ubicacion(self, ip, fabricante, tipo, gateway_ip):
        fabricante = (fabricante or "")
        tipo = (tipo or "")
        ip = (ip or "")
        if ip == gateway_ip:
            return "Gateway / Router principal"
        if "fortinet" in fabricante.lower():
            return "Firewall"
        if "impresora" in tipo.lower():
            return "Zona impresión"
        if "router" in tipo.lower() or "switch" in tipo.lower():
            return "Infraestructura de red"
        if "servidor" in tipo.lower():
            return "Zona servidores"
        if "móvil" in tipo.lower() or "tablet" in tipo.lower():
            return "Dispositivos móviles"
        if ip.startswith("169.254"):
            return "Sin DHCP"
        if ip.startswith("192.168"):
            return "Red local"
        return "Desconocido"
        
    """
    Realiza una observación pasiva de la red y guarda los resultados.
    No envía paquetes ICMP ni realiza escaneos de puertos por sockets.
    """
    def escanar_y_guardar(self, progress_callback=None):
        def update_progress(percentage, message):
            if progress_callback:
                progress_callback(percentage, message)

        update_progress(5, "Iniciando observación pasiva de la red...")
        rango = self.network.obtener_rango_ip()
        print ("Rango detectado:", rango)

        update_progress(15, "Leyendo tabla ARP del sistema...")
        # Eliminamos el barrido de ping para no enviar paquetes a las IPs
        dispositivos = self.network.obtener_dispositivos_desde_arp()
        print(f"Dispositivos encontrados en ARP: {len(dispositivos)}")

        if not dispositivos:
            update_progress(100, "No se encontraron dispositivos en la caché local.")
            return None

        update_progress(30, "Analizando conexiones activas del equipo monitor...")
        # Usamos psutil para ver conexiones reales sin enviar paquetes
        conexiones_por_ip = self.network.obtener_conexiones_observadas()

        historiales = []
        total = len(dispositivos)
       
        for idx, dispositivo in enumerate(dispositivos):
            ip = dispositivo.get("ip")
            update_progress(
                40 + int((idx / total) * 50),
                f"Procesando {ip} ({idx+1}/{total})..."
            )
            
            # ---- FABRICANTE ----
            fabricante = self.vendor.obtener_fabricante(dispositivo.get("mac"))
            
            # ---- COMPROBAR FABRICANTE ----
            self.alertas.comprobar_fabricante(
                {
                    "mac": dispositivo.get("mac"),
                    "ip": dispositivo.get("ip"),
                    "fabricante": fabricante
                }
            )
            
            # ---- CONEXIONES OBSERVADAS (PASIVO) ----
            puertos = conexiones_por_ip.get(ip, [
                {
                    "puerto": "No detectado",
                    "servicio": "Sin conexiones directas con monitor",
                    "estado": "Desconocido",
                    "pid": "-"
                }
            ])

            # ---- TIPO DISPOSITIVO ----
            tipo = self.classifier.clasificar(
                fabricante = fabricante,
                puertos = puertos,
                host_name = dispositivo.get("host_name")
            )
            # ---- RIESGO ----
            riesgo = (
                self.risk.calcular(
                    fabricante,
                    puertos,
                    tipo
                )
            )
            # ---- NOMBRE DISPOSITIVO ----
            host = dispositivo.get("host_name")
            if host and host!= "Desconocido":
                nombre_dispositivo = host
            elif fabricante and tipo:
                nombre_dispositivo = (
                    f"{fabricante} - {tipo}"
                )
            else:
                nombre_dispositivo = (
                    "Dispositivo desconocido"
                )
            # ---- VECES VISTO ----
            mac = dispositivo.get("mac")
            veces_visto = (
                self.repo.contar_por_mac(mac)
                + 1
            )
            # ---- COMPROBAR DISPOSITIVO NUEVO ----
            if veces_visto == 1:
                self.logs_repo.log_dispositivo_nuevo(
                    mac,
                    dispositivo.get("ip")
                )
                self.alertas.comprobar_dispositivo_nuevo(
                    dispositivo
                )
            # ---- PRIMER Y ULTIMO REGISTRO ----
            fecha_actual = dispositivo.get("fecha")

            primer_registro = (
                self.repo.buscar_primer_registro_por_mac(mac)
            )

            if primer_registro:
                primera_vez = (
                    primer_registro.get("primera_vez")
                    or primer_registro.get("primera_vez_conectado")
                    or primer_registro.get("fecha")
                )
            else:
                primera_vez = fecha_actual
            ultima_vez = fecha_actual
            
            # ---- COMPARAR CON ANTIMO REGISTRO ----
            actual_para_comparar = {
                "mac": mac,
                "ip": dispositivo.get("ip"),
                "riesgo": riesgo
            }
            self.comparador.comparar_con_anterior(
                primer_registro,
                actual_para_comparar
            )

            historial = Historial (
                ip = dispositivo.get("ip"),
                mac = dispositivo.get("mac"),
                veces_visto = veces_visto,
                host_name = dispositivo.get("host_name"),
                nombre_red = self.network.obtener_nombre_red(),
                gateway_ip = self.network.obtener_gateway(),
                rangos_ip = self.network.obtener_rango_ip(),
                puertos = puertos,
                fabricante = fabricante,
                tipo_dispositivo = tipo,
                riesgo = riesgo,
                nombre_dispositivo = nombre_dispositivo,
                ubicacion = self.obtener_ubicacion(
                    ip = dispositivo.get("ip"),
                    fabricante = fabricante,
                    tipo = tipo,
                    gateway_ip = self.network.obtener_gateway()
                ),
                fecha = dispositivo.get("fecha"),
                primera_vez = primera_vez,
                ultima_vez = ultima_vez
            )

            historiales.append(historial)

        # ---- BORRADO E INSERCIÓN DE ACTIVOS ----
        update_progress(95, "Guardando resultados en base de datos...")
        self.activos_repo.borrar_todo()
        
        if historiales:
            ids = self.repo.insertar_muchos(historiales)
            self.activos_repo.insertar_muchos(historiales)

            # ---- LOG ESCANEO COMPLETO ----
            self.logs_repo.log_escaneo_completo(
                len(ids),
                mac = self.network.obtener_mac_local(),
                ip = self.network.obtener_gateway(),
                nombre_red = self.network.obtener_nombre_red()
            )

            print("Registros insertados:", len(ids))
            update_progress(100, "Observación finalizada con éxito.")
            return ids

        print("No se encontraron dispositivos")
        update_progress(100, "No se detectaron dispositivos activos.")
        return None
