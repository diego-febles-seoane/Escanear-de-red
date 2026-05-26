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
    Escanea la red para obtener información de los dispositivos
    y los guarda en la base de datos Historial
    """
    def escanar_y_guardar(self, tipo_escaneo="normal"):
        rango = self.network.obtener_rango_ip()
        print ("Rango detectado:", rango)


        """
        Escanea cada IP en el rango para obtener información de los dispositivos en la red
        """
        for i in range(1, 255):
            ip = f"{rango}.{i}"
            self.network.hacer_ping(ip)


        dispositivos = self.network.obtener_dispositivos_desde_arp()


        historiales = []
       
        """
        Procesa cada dispositivo en la lista de dispositivos
        para obtener información de fabricante y guardarla en Historial
        """
        for dispositivo in dispositivos:
            
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
            # ---- PUERTOS ----
            ip = dispositivo.get("ip")
            if tipo_escaneo == "rapido":
                puertos = (
                    self.network
                    .obtener_puertos_rapido(ip)
                )
            elif tipo_escaneo == "completo":
                puertos = (
                    self.network
                    .obtener_puertos_completo(ip)
                )
            else:
                puertos = (
                    self.network
                    .obtener_puertos_normal(ip)
                )
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


        if historiales:
            ids = self.repo.insertar_muchos(historiales)

            # ---- BORRADO E INSERCIÓN DE ACTIVOS ----
            self.activos_repo.borrar_todo()
            self.activos_repo.insertar_muchos(historiales)

            # ---- LOG ESCANEO COMPLETO ----
            self.logs_repo.log_escaneo_completo(
                len(ids),
                mac = self.network.obtener_mac_local(),
                ip = self.network.obtener_gateway(),
                nombre_red = self.network.obtener_nombre_red()
            )

            print("Registros insertados:", len(ids))
            return ids


        print("No se encontraron dispositivos")
        return None