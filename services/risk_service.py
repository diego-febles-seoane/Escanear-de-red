"""
Clase para calcular el riesgo de un dispositivo
"""
class risk_service:
    def calcular(self, fabricante, puertos, tipo):
        resgo = "BAJO"
        puertos_peligrosos = [
            21, 23, 445, 3389, 5900
        ]
        for p in puertos:
            puerto = p.get("puerto")
            if puerto in puertos_peligrosos:
                resgo = "ALTO"
                break
        if fabricante == "Desconocido":
            resgo = "MEDIO"
        if tipo == "router":
            resgo = "MEDIO"
        return resgo