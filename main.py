from managers.network_manager import network_manager
from services.vendor_service import vendor_service
from services.device_classifier_service import device_classifier_service

network = network_manager()
vendor = vendor_service()
classifier = device_classifier_service()

dispositivo = network.obtener_info_interfaces()

for dispositivo in dispositivo:
    fabricante = (
        vendor.obtener_fabricante(
            dispositivo.get("mac")
        )
    )

    puertos = (
        network.obtener_puertos_por_agrupados_por_ip()
        .get(
            dispositivo.get("ip"),
            []
        )
    )
    tipo = (
        classifier.clasificar(
            fabricante=fabricante,
            puertos=puertos,
            host_name=dispositivo.get("host_name")
        )
    )

    print("\n==============")
    print("IP:", dispositivo.get("ip"))
    print("HOST:", dispositivo.get("host_name"))
    print("FABRICANTE:", fabricante)
    print("TIPO:", tipo)