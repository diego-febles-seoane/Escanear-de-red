from ctypes import addressof
import psutil
import socket
import subprocess
from datetime import datetime
import ipaddress

class network_manager:

    """
    Constructor de la clase NetworkManager
    """
    def __init__(self):
        print("Manager iniciado")
    """
    Metodo para obtener información de las interfaces de red actual y su dirección IP y MAC
    @return: Lista de diccionarios con información de las interfaces de red
    """
    def obtener_info_interfaces(self):
        interfaces = psutil.net_if_addrs()
        resultado = []
        """
        Recorrer las interfaces de red actual y obtener información de cada una
        @param nombre: Nombre de la interfaz de red
        @param direcciones: Lista de direcciones IP y MAC asociadas a la interfaz
        @return: Diccionario con información de la interfaz de red
        """
        for nombre, direcciones in interfaces.items():
            info = {
                "nombre_interfaz": nombre,
                "host_name": socket.gethostname(),
                "fecha": datetime.now(),
                "estado": "Activo",
                "ip": None,
                "mac": None,
                "rangos_ip": None
            }
            """
            Recorrer las direcciones IP y MAC asociadas a la interfaz
            @param direccion: Dirección IP o MAC
            @return: Diccionario con información de la dirección IP o MAC
            """
            for direccion in direcciones:
                if direccion.family == socket.AF_INET:
                    info["ip"] = direccion.address

                elif direccion.family == -1:
                    info["mac"] = direccion.address
            """
            Agregar la información de la interfaz a la lista de resultados si tiene una dirección IP o MAC
            """
            if info["ip"] or info["mac"]:
                resultado.append(info)
        return resultado

    """
    Metodo para hacer un ping a una dirección IP
    @param ip: Dirección IP a pingear
    @return: None
    """
    def hacer_ping(self, ip):
        comando = [
            "ping",
            "-n", "1",
            "-w", "500",
            ip
        ]
        """
        Ejecutar el comando ping y ignorar la salida
        @param comando: Comando a ejecutar
        @param stdout: Salida estándar a ignorar
        @param stderr: Salida de errores a ignorar
        """
        subprocess.run(
            comando,
            stdout = subprocess.DEVNULL,
            stderr = subprocess.DEVNULL
        )

    """
    Metodo para leer la tabla ARP actual  
    @return: Tabla ARP como cadena de texto
    """
    def leer_tabla_arp(self):   
        """
        Ejecutar el comando arp -a y capturar la salida
        @param comando: Comando a ejecutar
        @param capture_output: Capturar la salida
        @param text: Salida como texto
        @return: Tabla ARP como cadena de texto   
        """
        resultado = subprocess.run(
            ["arp", "-a"],
            capture_output = True,
            text = True
        )
        return resultado.stdout

    """
    Metodo para obtener el nombre de host de una dirección IP
    @param ip: Dirección IP a obtener el nombre de host
    @return: Nombre de host como cadena de texto
       """
    def obtener_hostname(self, ip):
        """
        Intentar obtener el nombre de host de la dirección IP
        @param ip: Dirección IP a obtener el nombre de host
        @return: Nombre de host como cadena de texto
        """
        try:
            nombre = socket.gethostbyaddr(ip)[0]
            return nombre
        except socket.herror:
            return None   
    """
    Metodo para obtener los dispositivos en la red ARP
    @return: Lista de diccionarios con información de los dispositivos en la red ARP
    """
    def obtener_dispositivos_desde_arp(self):
        tabla = self.leer_tabla_arp()
        dispositivos = []
        vistos = set()
        """
        Recorrer las líneas de la tabla ARP y obtener información de cada dispositivo
        @param linea: Línea de la tabla ARP
        @return: Diccionario con información de un dispositivo en la red ARP
        """
        for linea in tabla.splitlines():
            partes = linea.strip().split()
            """
            Si la línea no contiene información de un dispositivo, saltarla
            @return: None
            """
            if len(partes) < 3:
                continue
            ip = partes[0]
            mac = partes[1]
            tipo = partes[2]
            """
            Si la dirección IP y la dirección MAC son válidas, agregarla a la lista de dispositivos
            @return: None
            """
            if ip.count(".") == 3 and "-" in mac:
                clave = (ip, mac)

                if clave in vistos:
                    continue

                vistos.add(clave)

                dispositivos.append({
                    "ip": ip,
                    "gateway": self.obtener_gateway(),
                    "mac": mac,
                    "host_name": self.obtener_hostname(ip),
                    "tipo": tipo,
                    "fecha": datetime.now(),
                    "estado": "Activo"
                })
        return dispositivos 

    """
    Metodo para obtener el rango IP de la red
    @return: Rango IP como cadena de texto
    """
    def obtener_rango_ip(self):
        interfaces = psutil.net_if_addrs()

        for nombre, direcciones in interfaces.items():
            for direccion in direcciones:
                if direccion.family == socket.AF_INET:
                    ip = direccion.address

                    mascarara = direccion.netmask

                    red = ipaddress.IPv4Network(f"{ip}/{mascarara}", strict=False)


                    return str(red)
        return None

    """
    Metodo para obtener el gateway de la red
    @return: Gateway como cadena de texto
    """
    def obtener_gateway(self):
        resultado = subprocess.run(
            ["ipconfig"],
            capture_output=True,
            text=True
        )
        """
        Recorrer las líneas de la salida del ipconfig y obtener el gateway
        @param linea: Línea de la salida del ipconfig
        @return: Gateway como cadena de texto
        """
        for linea in resultado.stdout.splitlines():
            if "Puerta de enlace predeterminada" in linea:
                partes = linea.split(":")
                if len(partes) > 1:
                    gateway = partes[1].strip()
                    if gateway:
                        return gateway
        return None