"""
Clase para calcular el riesgo de un dispositivo con lógica avanzada
"""
class risk_service:
    def calcular(self, fabricante, puertos, tipo):
        riesgo_score = 0
        
        # 1. Análisis de Puertos (Puntuación acumulativa)
        puertos_criticos = {
            21: 20,   # FTP (Inseguro)
            23: 30,   # Telnet (Muy Inseguro)
            445: 25,  # SMB (Vulnerable a Ransomware)
            3389: 20, # RDP (Fuerza bruta)
            5900: 15, # VNC
            2049: 10, # NFS
            161: 10   # SNMP
        }
        
        puertos_abiertos = 0
        for p in puertos:
            puerto = p.get("puerto")
            if isinstance(puerto, int):
                puertos_abiertos += 1
                if puerto in puertos_criticos:
                    riesgo_score += puertos_criticos[puerto]
        
        # 2. Análisis de Fabricante
        fabricante_str = str(fabricante or "").lower()
        if fabricante_str == "desconocido" or not fabricante_str:
            riesgo_score += 15
        elif any(brand in fabricante_str for brand in ["hikvision", "dahua", "d-link"]):
            # Marcas con historial de vulnerabilidades IoT
            riesgo_score += 10

        # 3. Análisis de Tipo de Dispositivo
        tipo_str = str(tipo or "").lower()
        if "cam" in tipo_str or "iot" in tipo_str:
            riesgo_score += 15 # IoT suele ser menos seguro
        elif "server" in tipo_str:
            riesgo_score += 10 # Servidores son objetivos de alto valor
        elif "router" in tipo_str:
            riesgo_score += 5

        # 4. Cantidad de puertos abiertos
        if puertos_abiertos > 10:
            riesgo_score += 10
        elif puertos_abiertos > 5:
            riesgo_score += 5

        # Clasificación final basada en el score
        if riesgo_score >= 40:
            return "ALTO"
        elif riesgo_score >= 15:
            return "MEDIO"
        else:
            return "BAJO"
