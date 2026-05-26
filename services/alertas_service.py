from repositories.alertas_repository import alertas_repository
from repositories.historial_repository import historial_repository

"""
Clase para gestionar alertas
"""
class alertas_service:

    """
    Constructor de la clase
    """
    def __init__(self):
        self.repo = alertas_repository()
        self.historial = historial_repository()

    """
    Metodo para comprobar si un dispositivo es nuevo
    @param dispositivo: Diccionario con información del dispositivo
    @return: None
    """
    def comprobar_dispositivo_nuevo(self, dispositivo):
        mac = dispositivo.get("mac")
        existe = self.historial.buscar_por_mac(mac)
        if not existe:
            self.repo.guardar_alerta(
                tipo="DISPOSITIVO_NUEVO",
                mensaje=f"Nuevo dispositivo detectado en la red: {mac}",
                nivel="WARNING",
                mac=mac,
                ip=dispositivo.get("ip")
            )

    """
    Metodo para comprobar el fabricante de un dispositivo
    @param dispositivo: Diccionario con información del dispositivo
    @return: None
    """
    def comprobar_fabricante(self, dispositivo):
        fabricante = dispositivo.get("fabricante")
        if not fabricante or fabricante == "Desconocido":
            self.repo.guardar_alerta(
                tipo="FABRICANTE_DESCONOCIDO",
                mensaje="Fabricante no identificador",
                nivel="INFO",
                mac=dispositivo.get("mac"),
                ip=dispositivo.get("ip")
            )
