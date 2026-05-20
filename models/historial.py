"""
Clase para representar un registro de historial de red
"""
class Historial:
    """
    Constructor de la clase Historial con los siguientes parámetros: 
    @param nombre_red: Nombre de la red
    @param gateway_ip: Dirección IP del gateway
    @param puertos: Puertos abiertos en la red
    @param rangos_ip: Rangos de direcciones IP en la red
    @param ubicacion: Ubicación de la red
    @param tipo_dispositivo: Tipo de dispositivo en la red
    @param fecha: Fecha de la entrada en el historial
    @param host_name: Nombre del host en la red
    @param ip: Dirección IP del host en la red
    @param mac: Dirección MAC del host en la red
    @param fabricante: Fabricante del dispositivo en la red
    @param nombre_dispositivo: Nombre del dispositivo en la red
    @param estado: Estado del dispositivo en la red
    @param primera_vez: Fecha de la primera vez que se detectó el dispositivo
    @param ultima_vez: Fecha de la última vez que se detectó el dispositivo
    """
    def __init__(
        self,
        nombre_red = None,
        gateway_ip = None,
        puertos = None,   
        rangos_ip = None, 
        ubicacion = None,
        tipo_dispositivo = None,
        fecha = None,
        host_name = None,
        ip = None,
        mac = None,
        fabricante = None,
        nombre_dispositivo = None,
        estado = None,
        primera_vez = None,
        ultima_vez = None,
        ):
        self.nombre_red = nombre_red
        self.gateway_ip = gateway_ip
        self.puertos = puertos
        self.rangos_ip = rangos_ip
        self.ubicacion = ubicacion
        self.tipo_dispositivo = tipo_dispositivo
        self.fecha = fecha
        self.host_name = host_name
        self.ip = ip
        self.mac = mac
        self.fabricante = fabricante
        self.nombre_dispositivo = nombre_dispositivo
        self.estado = estado
        self.primera_vez = primera_vez
        self.ultima_vez = ultima_vez
    
    """
    Método para convertir el objeto Historial a un diccionario
    @return: Diccionario con los atributos del objeto Historial
    """
    def to_dict(self):
        return {
            "nombre_red": self.nombre_red,
            "gateway_ip": self.gateway_ip,
            "puertos": self.puertos,
            "rangos_ip": self.rangos_ip,
            "ubicacion": self.ubicacion,
            "tipo_dispositivo": self.tipo_dispositivo,
            "fecha": self.fecha,
            "host_name": self.host_name,
            "ip": self.ip,
            "mac": self.mac,
            "fabricante": self.fabricante,
            "nombre_dispositivo": self.nombre_dispositivo,
            "estado": self.estado,
            "primera_vez": self.primera_vez,
            "ultima_vez": self.ultima_vez,
        }