from ctypes import addressof
import psutil
import socket
import subprocess
from datetime import datetime
import ipaddress
import os
import re
"""
Clase network_manager que controla la lectura de datos con Scapy
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

    # ---- CONEXION A LA RED ----
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

    # ---- LECTOR DE TABLA ARP ----
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

    # ---- INFORMACION DEL HOST ----
    """
    Metodo para obtener el nombre de host de una dirección IP
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

        """
        Intentar obtener el nombre de host utilizando el comando nbtstat -A
        @param ip: Dirección IP a obtener el nombre de host
        @return: Nombre de host como cadena de texto
        """
        try:
            resultado = subprocess.run(
                ["nbtstat," "-A", ip],
                capture_output=True,
                text=True,
                timeout=3
            )
            
            """
            Recorrer las líneas de la salida del comando nbtstat -A y obtener el nombre de host
            @param linea: Línea de la salida del comando nbtstat -A
            @return: Nombre de host como cadena de texto
            """
            for linea in resultado.stdout.splitlines():
                if "<00>" in linea and "UNIQUE" in linea:
                    partes = linea.split()

                    if len(partes) > 0:
                        return partes[0]
        except:
            pass

        return "Desconocido"
    
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

    # ---- INFORMACION DEL RANGO IP ----
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
                    mascara = direccion.netmask
                    if ip.startswith("224."):
                        continue

                    if ip.startswith("239."):
                        continue

                    if ip == "255.255.255.255":
                        continue

                    if ip.endswith(".255"):
                        continue
                    red = ipaddress.IPv4Network(
                        f"{ip}/{mascara}",
                        strict=False
                    )
                    return str(red)
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
    
    # ---- ESCANEO DE PUERTOS ----
    """
    Metodo para obtener los puertos abiertos en un rango de puertos
    @param ip: Dirección IP a escanear
    @param inicio: Puerto de inicio del rango
    @param fin: Puerto de fin del rango
    @return: Lista de diccionarios con información de los puertos abiertos
    """
    def obtener_puertos_abiertos_rango(self, ip, inicio, fin):
        puertos_abiertos = []

        for puerto in range(inicio, fin + 1):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.2)

            resultado = sock.connect_ex((ip, puerto))

            if resultado == 0:
                puertos_abiertos.append({
                    "puerto": puerto,
                    "servicio": self.obtener_servicio_puerto(puerto),
                    "estado": "ABIERTO",
                    "pid": "-"
                })

            sock.close()

        if not puertos_abiertos:
            return [
                {
                    "puerto": "No detectado",
                    "servicio": "Sin puertos abiertos en el rango",
                    "estado": "Desconocido",
                    "pid": "-"
                }
            ]

        return puertos_abiertos
    
    """
    Metodo para obtener los puertos abiertos en el rango 1-1024
    @param ip: Dirección IP a escanear
    @return: Lista de diccionarios con información de los puertos abiertos
    """
    def obtener_puertos_rapido(self, ip):
        puertos_importantes = [
            21, 22, 23, 53, 80, 135, 139,
            443, 445, 3389, 5900, 8080, 9100
        ]
        return self.obtener_puertos_lista(
            ip,
            puertos_importantes
        )

    """
    Metodo para obtener los puertos abiertos en el rango 1-5000
    @param ip: Dirección IP a escanear
    @return: Lista de diccionarios con información de los puertos abiertos
    """
    def obtener_puertos_normal(self, ip):
        return self.obtener_puertos_abiertos_rango(
            ip,
            1,
            5000
        )

    """
    Metodo para obtener los puertos abiertos en el rango 1-65535
    @param ip: Dirección IP a escanear
    @return: Lista de diccionarios con información de los puertos abiertos
    """
    def obtener_puertos_completo(self, ip):
        return self.obtener_puertos_abiertos_rango(
            ip,
            1,
            65535
        )
    """
    Metodo para obtener los puertos abiertos en una lista de puertos
    @param ip: Dirección IP a escanear
    @param lista_puertos: Lista de puertos a escanear
    @return: Lista de diccionarios con información de los puertos abiertos
    """
    def obtener_puertos_lista(self, ip, lista_puertos):
        puertos_abiertos = []

        for puerto in lista_puertos:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.05)

            resultado = sock.connect_ex((ip, puerto))

            if resultado == 0:
                puertos_abiertos.append({
                    "puerto": puerto,
                    "servicio": self.obtener_servicio_puerto(puerto),
                    "estado": "ABIERTO",
                    "pid": "-"
                })

            sock.close()

        if not puertos_abiertos:
            return [
                {
                    "puerto": "No detectado",
                    "servicio": "Sin puertos abiertos detectados",
                    "estado": "Desconocido",
                    "pid": "-"
                }
            ]

        return puertos_abiertos
    # ---- FINAL DE ESCANEOS DE LOS PUERTOS ----

    # ---- DE MOMENTO NO SE USA ----
    """
    Metodo para obtener los puertos en la red local
    @return: Diccionario con los puertos en la red local
    """
    def obtener_puertos_red_local(self):
        puertos = self.obtener_puertos_por_agrupados_por_ip()
        red_local = self.obtener_prefijo_red_local()
        resultado = {}
        if not red_local:
            return resultado
        for ip,lista_puertos in puertos.items():
            try:
                ip_obj = ipaddress.IPv4Address(ip)
            except:
                continue

            if ip_obj in red_local:
                resultado[ip] = lista_puertos

        return resultado
    # ---- DE MOMENTO NO SE USA ----
    """
    Metodo para obtener los puertos en uso
    @return: Lista de diccionarios con información de los puertos en uso
    """
    def obtener_puertos_en_uso(self):
        conexiones = psutil.net_connections(kind="inet")
        puertos = []

        for conexion in conexiones:
            if not conexion.laddr:
                continue
            local_ip = conexion.laddr.ip
            local_puerto = conexion.laddr.port

            remote_ip = None
            remote_puerto = None

            if conexion.raddr:
                remote_ip = conexion.raddr.ip
                remote_puerto = conexion.raddr.port

            puertos.append({
                "local_ip": local_ip,
                "local_puerto": local_puerto,
                "remote_ip": remote_ip,
                "remote_puerto": remote_puerto,
                "estado": conexion.status,
                "pid": conexion.pid,
                "servicio_local": self.obtener_servicio_puerto(local_puerto)
            })
        return puertos
    # ---- DE MOMENTO NO SE USA ----
    """
    Metodo para obtener los puertos por agrupados por IP
    @return: Diccionario con los puertos agrupados por IP
    """
    def obtener_puertos_por_agrupados_por_ip(self):
        conexiones = self.obtener_puertos_en_uso()
        agrupados = {}

        for conexion in conexiones:
            pares = [
                {
                    "ip": conexion.get("local_ip"),
                    "puerto": conexion.get("local_puerto"),
                }
                ,
                {
                    "ip": conexion.get("remote_ip"),
                    "puerto": conexion.get("remote_puerto"),
                }
            ]
            for par in pares:
                ip = par["ip"]
                puerto = par["puerto"]

                if not ip or not puerto:
                    continue
                if ip not in agrupados:
                    agrupados[ip] = []

                registro = {
                    "puerto": puerto,
                    "servicio": self.obtener_servicio_puerto(puerto),
                    "estado": conexion.get("estado"),
                    "pid": conexion.get("pid"),
                }

                if registro not in agrupados[ip]:
                    agrupados[ip].append(registro)

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