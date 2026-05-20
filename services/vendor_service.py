import requests
import time
from repositories.fabricante_repository import fabricnate_repository
"""
Servicio de obtener información de fabricantes de dispositivos
"""
class vendor_service:

    """
    Clase para obtener información de fabricantes de dispositivos
    """
    def __init__(self):
        self.fabricnate_repository = fabricnate_repository()

    """
    Obtiene el OUI de una dirección MAC
    """
    def obtener_oui(self, mac):
        if not mac:
            return None

        mac_limpia = mac.replace("-", ":").upper()
        partes = mac_limpia.split(":")

        if len(partes) < 3:
            return None

        return ":".join(partes[:3])

    """
    Consulta la API de obtener información de fabricante
    """
    def consultar_api(self, oui):

        url = f"https://api.macvendors.com/{oui}"
        respuesta = requests.get(url, timeout=5)
        
        if respuesta.status_code == 200:
            return respuesta.text
        return "Desconocido"

    """
    Obtiene el nombre del fabricante de un dirección MAC
    """
    def obtener_fabricante(self, mac):
        oui = self.obtener_oui(mac)

        if not oui:
            return None
        
        fabricante_guardado = self.fabricnate_repository.buscar_por_oui(oui)

        if fabricante_guardado:
            return fabricante_guardado["fabricante"]

        fabricante = self.consultar_api(oui)

        if fabricante != "Desconocido":
            self.fabricnate_repository.insertar_fabricante(oui, fabricante)

        time.sleep(1)
        return fabricante



