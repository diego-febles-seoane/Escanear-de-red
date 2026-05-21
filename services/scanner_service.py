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

            tipo = self.classifier.clasificar(
                fabricante = fabricante,
                puertos = puertos,
                host_name = dispositivo.get("host_name")
            )
            
            fabricante = self.vendor.obtener_fabricante(dispositivo.get("mac"))

            historial = Historial (
                ip = dispositivo.get("ip"),
                mac = dispositivo.get("mac"),
                host_name = dispositivo.get("host_name"),
                nombre_red = self.network.obtener_nombre_red(),
                gateway_ip = self.network.obtener_gateway(),
                rangos_ip = self.network.obtener_rango_ip(),
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
                fabricante = fabricante,
                tipo_dispositivo = tipo,
                fecha = dispositivo.get("fecha"),
                estado = dispositivo.get("estado"),
            )

            historiales.append(historial)
            print(historial.puertos)

        if historiales: 
            ids = self.repo.insertar_muchos(historiales)
            print("Registros insertados:", len(ids))
            return ids

        print("No se encontraron dispositivos")
        return None
