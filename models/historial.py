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
        ip = None,
        mac = None,
        veces_visto = None,
        host_name = None,
        nombre_red = None,
        gateway_ip = None,
        rangos_ip = None, 
        puertos = None,   
        fabricante = None,
        tipo_dispositivo = None,
        nombre_dispositivo = None,
        estado = None,
        ubicacion = None,
        fecha = None,
        primera_vez = None,
        ultima_vez = None,
        ):
        self.ip = ip
        self.mac = mac
        self.veces_visto = veces_visto
        self.host_name = host_name
        self.nombre_red = nombre_red
        self.gateway_ip = gateway_ip
        self.rangos_ip = rangos_ip
        self.puertos = puertos
        self.ubicacion = ubicacion
        self.tipo_dispositivo = tipo_dispositivo
        self.nombre_dispositivo = nombre_dispositivo
        self.fecha = fecha
        self.fabricante = fabricante
        self.estado = estado
        self.primera_vez = primera_vez
        self.ultima_vez = ultima_vez
    
    """
    Método para convertir el objeto Historial a un diccionario
    @return: Diccionario con los atributos del objeto Historial
    """
    def to_dict(self):
        return {
            "ip": self.ip,
            "mac": self.mac,
            "veces_visto": self.veces_visto,
            "host_name": self.host_name,
            "nombre_red": self.nombre_red,
            "gateway_ip": self.gateway_ip,
            "rangos_ip": self.rangos_ip,
            "puertos": self.puertos,
            "fabricante": self.fabricante,
            "tipo_dispositivo": self.tipo_dispositivo,
            "nombre_dispositivo": self.nombre_dispositivo,
            "estado": self.estado,
            "ubicacion": self.ubicacion,
            "fecha": self.fecha,
            "primera_vez": self.primera_vez,
            "ultima_vez": self.ultima_vez,
        }