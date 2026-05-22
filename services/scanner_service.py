from managers.network_manager import network_manager
from models.historial import Historial
from repositories.historial_repository import historial_repository
from services.vendor_service import vendor_service
from services.device_classifier_service import device_classifier_service

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
    def escanar_y_guardar(self):
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
        puertos_por_ip = self.network.obtener_puertos_por_agrupados_por_ip()


        for dispositivo in dispositivos:


            # ---- FABRICANTE ----
            fabricante = self.vendor.obtener_fabricante(dispositivo.get("mac"))
            # ---- PUERTOS ----
            puertos = (
                    puertos_por_ip.get(
                        dispositivo.get("ip"),
                        []
                    )
                    or [
                        {
                            "puerto": "Puertos desconocidos o inaccesibles",
                            "servicio": "Sin tráfico observado",
                            "estado": "Inactivo",
                            "pid": "Sin PID asignado"
                        }
                    ]
                ),
            # ---- TIPO DISPOSITIVO ----
            tipo = self.classifier.clasificar(
                fabricante = fabricante,
                puertos = puertos,
                host_name = dispositivo.get("host_name")
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
                +1
            )
            # ---- PRIMER Y ULTIMO REGISTRO ----
            mac = dispositivo.get("mac")
            fecha_actual = dispositivo.get("fecha")
            primer_registro = (
                self.repo.buscar_primer_registro_por_mac(mac)
            )
            if primer_registro:
                primera_vez = primer_registro.get(
                    "primera_vez_conectado"
                ) or primer_registro.get(
                    "fecha"
                )
            else:
                primera_vez = fecha_actual
            ultima_vez = fecha_actual

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
            print("Registros insertados:", len(ids))
            return ids


        print("No se encontraron dispositivos")
        return None



