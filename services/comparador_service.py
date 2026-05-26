from repositories.alertas_repository import alertas_repository

"""
Servicio de comparador.
"""
class comparador_service:

    """
    Constructor del servicio de comparador.
    """
    def __init__(self):
        self.alertas_repo = alertas_repository()
    
    """
    Compara dos activos para detectar cambios en su IP o riesgo.
    Si hay cambios, se generan alertas.
    :param anterior: El activo anterior para comparar.
    :param actual: El activo actual para comparar.
    """
    def comparar_con_anterior(self, anterior, actual):
        if not anterior:
            return
        mac = actual.get("mac")
        ip_actual = actual.get("ip")
        ip_anterior = anterior.get("ip")
        riesgo_actual = actual.get("riesgo")
        riesgo_anterior = anterior.get("riesgo")
        if ip_anterior != ip_actual:
            self.alertas_repo.guardar_alerta(
                tipo="CAMBIO_IP",
                mensaje=f"La MAC {mac} cambió de IP: {ip_anterior} --> {ip_actual}",
                nivel="INFO",
                mac=mac,
                ip=ip_actual,
            )
        if riesgo_anterior != riesgo_actual:
            self.alertas_repo.guardar_alerta(
                tipo="CAMBIO_RIESGO",
                mensaje=f"La MAC {mac} cambió de riesgo: {riesgo_anterior} --> {riesgo_actual}",
                nivel="WARNING",
                mac=mac,
                ip=ip_actual,
            )
