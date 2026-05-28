
import sys
from datetime import datetime
import subprocess
import re


def probar_ping(ip):
    """Función simple para probar ping manualmente"""
    try:
        resultado = subprocess.run(
            ["ping", "-n", "1", "-w", "500", ip],
            capture_output=True,
            text=True,
            timeout=2
        )
        return resultado.returncode == 0
    except:
        return False


def obtener_fabricante_simple(mac):
    """Función simple para obtener fabricante sin base de datos"""
    if not mac or mac == "Desconocida":
        return "Desconocido"
    # OUI lookup básico (solo algunos ejemplos)
    oui = mac[:8].upper()
    oui_dict = {
        "00:11:22": "Cisco Systems",
        "AA:BB:CC": "Dell Inc.",
        "00:1A:2B": "HP",
        "00:1C:42": "VMware",
        "00:50:56": "VMware",
        "00:0C:29": "VMware",
        "00:15:5D": "Microsoft",
        "00:00:5E": "IANA",
        "00:1B:C0": "Juniper",
        "00:1D:72": "Cisco-Linksys"
    }
    return oui_dict.get(oui, "Desconocido")


def clasificar_dispositivo_simple(fabricante, puertos, host_name):
    """Función simple para clasificar dispositivo"""
    host = (host_name or "").lower()
    fab = (fabricante or "").lower()
    
    if "router" in host or "gateway" in host or "cisco" in fab:
        return "Router / Gateway"
    if "print" in host or "impresora" in host:
        return "Impresora"
    if "phone" in host or "teléfono" in host:
        return "Teléfono"
    if "servidor" in host or "server" in host:
        return "Servidor"
    if "pc" in host or "desktop" in host or "laptop" in host:
        return "PC / Laptop"
    if any(p.get("puerto") in [22, 23, 135, 139, 445, 3389] for p in (puertos or [])):
        return "PC / Laptop"
    return "Dispositivo genérico"


def calcular_riesgo_simple(fabricante, puertos, tipo):
    """Función simple para calcular riesgo"""
    riesgo = "Bajo"
    # Revisar puertos
    puertos_riesgo = [22, 23, 135, 139, 443, 445, 3389]
    for p in (puertos or []):
        puerto = p.get("puerto")
        if isinstance(puerto, int) and puerto in puertos_riesgo:
            riesgo = "Medio"
    if tipo in ["Servidor", "Router / Gateway"]:
        riesgo = "Alto"
    return riesgo


def main():
    print("=== Iniciando escaneo de red (modo Ethernet sin internet) ===")
    
    # Configurar red manualmente (ya que sabemos que es 192.168.1.x)
    RANGO_RED = "192.168.1"  # Ajusta esto si tu red es diferente
    IP_PRUEBA = "192.168.1.20"  # La IP que sabes que existe
    
    try:
        # Importar solo network_manager, que no necesita base de datos
        from managers.network_manager import network_manager
        
        # Inicializar solo network_manager
        network = network_manager()
        
        # Paso 1: Mostrar interfaces de red disponibles
        print("\n[+] Interfaces de red disponibles:")
        interfaces = network.obtener_info_interfaces()
        for iface in interfaces:
            print(f"  - {iface['nombre_interfaz']}: IP={iface['ip']}, MAC={iface['mac']}")
        
        # Paso 2: Probar ping a la IP conocida
        print(f"\n[+] Probando ping a {IP_PRUEBA}...")
        ping_ok = probar_ping(IP_PRUEBA)
        print(f"  Resultado: {'OK' if ping_ok else 'FALLIDO'}")
        
        # Paso 3: Hacer ping sweep manual en el rango conocido
        print(f"\n[+] Realizando ping sweep en {RANGO_RED}.x...")
        dispositivos_encontrados = set()
        
        # Primero pingueamos la IP que sabemos que existe
        if probar_ping(IP_PRUEBA):
            dispositivos_encontrados.add(IP_PRUEBA)
        
        # Luego pingueamos el resto del rango (más rápido con menos hilos)
        from concurrent.futures import ThreadPoolExecutor, as_completed
        ips = [f"{RANGO_RED}.{i}" for i in range(1, 255)]
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(probar_ping, ip): ip for ip in ips}
            for future in as_completed(futures):
                ip = futures[future]
                if future.result():
                    dispositivos_encontrados.add(ip)
                    print(f"  Encontrado: {ip}")
        
        print(f"\n[+] IPs respondiendo a ping: {len(dispositivos_encontrados)}")
        
        # Paso 4: Leer tabla ARP (esto debería capturar todos los dispositivos en Ethernet
        print("\n[+] Leyendo tabla ARP...")
        dispositivos_arp = network.obtener_dispositivos_desde_arp()
        print(f"  Dispositivos en ARP: {len(dispositivos_arp)}")
        
        # Combinar resultados: dispositivos de ARP + los que respondieron a ping
        dispositivos = dispositivos_arp.copy()
        ips_arp = {d["ip"] for d in dispositivos_arp}
        
        # Agregar dispositivos que respondieron a ping pero no están en ARP
        for ip in dispositivos_encontrados:
            if ip not in ips_arp:
                dispositivos.append({
                    "ip": ip,
                    "mac": "Desconocida",
                    "host_name": network.obtener_hostname(ip),
                    "fecha": datetime.now()
                })
        
        # Si todavía no hay dispositivos, usar la IP de prueba como mínimo
        if not dispositivos:
            print("\n[!] Aún no hay dispositivos. Agregando la IP de prueba...")
            dispositivos.append({
                "ip": IP_PRUEBA,
                "mac": "Desconocida",
                "host_name": network.obtener_hostname(IP_PRUEBA),
                "fecha": datetime.now()
            })
        
        # Paso 5: Procesar y mostrar información
        print(f"\n=== Dispositivos encontrados: {len(dispositivos)}")
        for idx, dispositivo in enumerate(dispositivos, 1):
            ip = dispositivo.get("ip")
            mac = dispositivo.get("mac")
            host_name = dispositivo.get("host_name")
            fecha = dispositivo.get("fecha")
            
            # Obtener fabricante (función simple
            fabricante = obtener_fabricante_simple(mac)
            
            # Escanear puertos
            try:
                puertos = network.obtener_puertos_rapido(ip)
            except Exception as e:
                print(f"  Error al escanear puertos para {ip}: {e}")
                puertos = []
            
            # Clasificar dispositivo
            tipo = clasificar_dispositivo_simple(fabricante, puertos, host_name)
            
            # Calcular riesgo
            nivel_riesgo = calcular_riesgo_simple(fabricante, puertos, tipo)
            
            # Mostrar información
            print(f"\n  {'='*50}")
            print(f"  Dispositivo {idx}:")
            print(f"  {'='*50}")
            print(f"  IP:              {ip}")
            print(f"  MAC:             {mac}")
            print(f"  Hostname:        {host_name or 'Desconocido'}")
            print(f"  Fabricante:      {fabricante}")
            print(f"  Tipo:            {tipo}")
            print(f"  Riesgo:          {nivel_riesgo}")
            print(f"  Fecha:           {fecha}")
            print(f"  Puertos abiertos:")
            if puertos and len(puertos) > 0 and puertos[0].get("puerto") != "No detectado":
                for p in puertos[:5]:  # Mostrar hasta 5 puertos
                    print(f"                   - {p.get('puerto')}: {p.get('servicio')} ({p.get('estado')})")
            else:
                print(f"                   Ninguno")
    
    except Exception as e:
        print(f"\n[!] Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n=== Escaneo completo ===")


if __name__ == "__main__":
    main()
