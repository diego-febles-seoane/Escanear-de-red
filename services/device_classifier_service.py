"""
Clase para clasificar dispositivos en base a su fabricante, puertos y nombre de host
"""
class device_classifier_service:

    """
    Clasifica un dispositivo en base a su fabricante, puertos y nombre de host
    @param fabricante: Fabricante del dispositivo
    @param puertos: Lista de puertos abiertos
    @param host_name: Nombre del host
    @return: Clasificación del dispositivo
    """
    def clasificar(self, fabricante=None, puertos=None, host_name=None):
        fabricante = (fabricante or "").lower()
        host_name = (host_name or "").lower()
        puertos = puertos or []

        numero_puertos = []

        for puerto in puertos:

            if not isinstance(puerto, dict):
                continue
            valor = puerto.get("puerto")

            if isinstance(valor, int):
                numero_puertos.append(valor)
        
        # ---- IMPRESORAS ----
        if (
            "printer" in host_name
            or "impresora" in host_name
            or 9100 in numero_puertos
        ):
            return "Impresora"
        # ---- WINDOWS ----
        if 3389 in numero_puertos:
            return "Windows"
        # ---- SSH ----
        if 22 in numero_puertos:
            return "SSH"
        # ---- ROUTERS ----
        if (
            "router" in host_name
            or "switch" in host_name
            or "ap" in host_name
        ):
            return "Router / Switch"
        # ---- WEB ----
        if(
            80 in numero_puertos
            or 443 in numero_puertos
        ):
            return "Servidor web / Paner web"
        
        # ---- FABRICANTES RED ----
        if any(
            marca in fabricante for marca in ["cisco", "tp-link", "ubiquiti", "mikrotik", "netgear", "aruba"]
        ):
            return "Dispositivo red"
        
        # ---- FABRICANTES PC ----
        if any(
            marca in fabricante for marca in ["intel", "dell", "lenovo", "acer", "asus", "hewlett", "hp"]
        ):
            return "Ordenador"

        # ---- MOVILES ----
        if any(
            marca in fabricante for marca in ["apple", "samsung", "xiaomi", "oppo", "huawei", "nokia", "motorola", "lg"]
        ):
            return "Dispositivo movil / tablet"
        
        # ---- CUALQUIER FABRICANTE ----
        if fabricante:
            return (
                "Dispositivo " + fabricante.title()
            )
        return (
            "Dispositivo desconocido"
        )
