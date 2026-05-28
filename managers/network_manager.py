import psutil
import socket
import subprocess
from datetime import datetime
import ipaddress
import os
import re
"""
Clase network_manager que controla la lectura de datos de red
"""
class network_manager:

    """
    Constructor de la clase NetworkManager
    """
    def __init__(self):
        print("Manager iniciado")

    # ---- INFORMACION DE LAS INTERFACES DE RED ----
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

    # ---- OBTENER MAC LOCAL PARA LOS REGISTROS DE LOGS ----
    """
    Metodo para obtener la dirección MAC local del equipo actual
    @return: Dirección MAC local como cadena de texto
    """
    def obtener_mac_local(self):
        salida = subprocess.check_output(
            "ipconfig /all"
        ).decode(
            errors="ignore"
        )
        mac = re.search(
            r"([0-9A-F]{2}"
            r"[-:]"
            r"){5}"
            r"([0-9A-F]{2})",
            salida,
            re.I
        )
        if mac:
            return mac.group()
        return None

    # ---- CONEXION A LA RED (PASIVA) ----
    """
    Metodo para obtener el nombre de host de una dirección IP (Solo si está en caché DNS local)
    @param ip: Dirección IP a obtener el nombre de host
    @return: Nombre de host como cadena de texto
    """
    def obtener_hostname(self, ip):
        try:
            nombre = socket.gethostbyaddr(ip)[0]
            if nombre:
                return nombre
        except:
            pass
        return "Desconocido"

    # ---- LECTOR DE TABLA ARP ----
    """
    Metodo para leer la tabla ARP actual  
    @return: Tabla ARP como cadena de texto
    """
    def leer_tabla_arp(self):   
        resultado = subprocess.run(
            ["arp", "-a"],
            capture_output = True,
            text = True
        )
        return resultado.stdout
    
       # ---- LEER DISPOSITIVOS DESDE LA TABLA ARP ----
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
            if len(partes) < 3:
                continue
            
            ip = partes[0]
            mac_raw = partes[1]
            tipo = partes[2]

            # Limpiar la MAC (quitar paréntesis si los hay y convertir a formato estándar)
            mac = mac_raw.replace("(", "").replace(")", "").replace("-", ":").lower()
            
            # Validar IP y MAC
            es_ip = re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", ip)
            # Aceptamos formatos de MAC con o sin ceros a la izquierda (Windows a veces los quita en arp -a)
            es_mac = re.match(r"^([0-9a-f]{1,2}[:]){5}([0-9a-f]{1,2})$", mac)

            if es_ip and es_mac:
                # Normalizar MAC a 00:00:00:00:00:00
                mac_parts = mac.split(":")
                mac = ":".join([p.zfill(2) for p in mac_parts])
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
        if not dispositivos:
            print("No se encontraron dispositivos válidos en la tabla ARP. Contenido raw:")
            print(tabla[:500]) # Mostrar solo el principio para no saturar
        return dispositivos 

    # ---- INFORMACION DEL RANGO IP ----
    """
    Metodo para obtener el rango IP de la red
    @return: Rango IP como cadena de texto
    """
    def obtener_rango_ip(self):
        interfaces = psutil.net_if_addrs()
        for nombre, direcciones in interfaces.items():
            for direccion in direcciones:
                if direccion.family != socket.AF_INET:
                    continue
                ip = direccion.address
                mascara = direccion.netmask
                if not ip or not mascara:
                    continue
                if ip.startswith("127."):
                    continue
                if ip.startswith("169.254."):
                    continue
                if ip.startswith("224."):
                    continue
                if ip.startswith("239."):
                    continue
                if ip == "0.0.0.0":
                    continue
                if ip == "255.255.255.255":
                    continue
                red = ipaddress.IPv4Network(
                    f"{ip}/{mascara}",
                    strict=False
                )
                # Devolvemos solo la parte de la red sin la máscara para el ping sweep antiguo
                return str(red.network_address).rsplit('.', 1)[0]
        return None

    """
    Metodo para obtener el servicio de un puerto
    @param puerto: Puerto a buscar
    @return: Nombre del servicio o "Desconocido" si no se encuentra
    """
    def obtener_servicio_puerto(self, puerto, protocolo="tcp"):
        try:
            return socket.getservbyport(puerto, protocolo)
        except:
            return "Desconocido"

    """
    Metodo para obtener el prefijo de la red local
    @return: Prefijo de la red local como cadena de texto
    """
    def obtener_prefijo_red_local(self):
        rango = self.obtener_rango_ip()

        if not rango:
            return None

        red = ipaddress.IPv4Network(
            rango,
            strict=False
        )
        return red
    
    # ---- CONEXIONES OBSERVADAS ----
    """
    Metodo para obtener las conexiones observadas desde el equipo monitor
    @return: Diccionario con los puertos agrupados por IP
    """
    def obtener_conexiones_observadas(self):
        conexiones = psutil.net_connections(kind="inet")
        agrupados = {}

        for conexion in conexiones:
            if not conexion.laddr:
                continue
            
            # Solo nos interesan conexiones que tengan una dirección remota (observadas)
            if not conexion.raddr:
                continue

            remote_ip = conexion.raddr.ip
            remote_puerto = conexion.raddr.port
            local_puerto = conexion.laddr.port

            if remote_ip not in agrupados:
                agrupados[remote_ip] = []

            registro = {
                "puerto": remote_puerto,
                "servicio": self.obtener_servicio_puerto(remote_puerto),
                "estado": conexion.status,
                "pid": conexion.pid,
                "puerto_local": local_puerto
            }

            if registro not in agrupados[remote_ip]:
                agrupados[remote_ip].append(registro)

        for ip in agrupados:
            agrupados[ip] = sorted(
                agrupados[ip],
                key = lambda x: x["puerto"],
            )
        return agrupados

    # ---- INFORMACION DEL GATEWAY ----
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

    # ---- INFORMACION DEL NOMBRE DE RED ----
    
    def obtener_nombre_red(self):
        dominio = os.getenv(
            "USERDOMAIN"
        )
        if dominio and dominio.upper() not in ["RED", "WORKGROUP"]:
            return dominio
        
        fqdn = socket.getfqdn()

        if fqdn and fqdn != socket.gethostname():
            return fqdn
        
        gateway = (
            self.obtener_gateway()
        )
        if gateway:
            return (
                f"RED-{gateway}"
            )
        rango = (
            self.obtener_rango_ip()
        )
        if rango:
            return (
                f"RED-{rango}"
            )
        return (
            "Red desconocida"
        )