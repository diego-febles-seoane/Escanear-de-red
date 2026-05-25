import csv
import json
from managers.mongo_manager import mongo_manager
from datetime import datetime
from openpyxl import Workbook

"""
Exportar datos a archivos JSON y CSV
"""
class export_service:

    """
    Exportar datos a un archivo JSON
    """
    def exportar_json(self, datos, ruta):
        with open(ruta, "w", encoding="utf-8") as archivo:
            json.dump(
                datos,
                archivo,
                indent=4,
                ensure_ascii=False,
                default=str
            )
        return ruta

    """
    Exportar datos a un archivo CSV
    """
    def exportar_csv(self, datos, ruta):
        if not datos:
            return None

        columnas = datos[0].keys()

        with open(ruta, "w", encoding="utf-8") as archivo:
            writer = csv.DictWriter(archivo, fieldnames=columnas)
            writer.writeheader()
            writer.writerows(datos)
        return ruta

    """
    Limpiar valores para exportar a Excel
    @param valor: Valor a limpiar
    @return: Valor limpio
    """
    def limpiar_valor_excel(self, valor):
        if isinstance(valor, list) or isinstance(valor, dict):
            return str(valor)
        return valor

    """
    Exportar datos a un archivo Excel con valores limpios
    @param datos: Lista de objetos JSON
    @param ruta: Ruta del archivo Excel
    @return: Ruta del archivo Excel
    """
    def exportar_excel(self, datos, ruta):
        if not datos:
            return None
        workbook = Workbook()
        hoja = workbook.active
        hoja.title = "Resultados"
        columnas = list(datos[0].keys())
        hoja.append(columnas)

        for fila in datos:
            hoja.append(
                [
                    self.limpiar_valor_excel(valor)
                    for valor in fila.values()
                ]
            )

        workbook.save(ruta)
        return ruta

    """
    Obtener todos los datos de una colección en la base de datos
    @param nombre_coleccion: Nombre de la colección en la base de datos
    @param fecha_desde: Fecha desde la cual obtener los datos
    @param fecha_hasta: Fecha hasta la cual obtener los datos
    @param limite: Limite de datos a obtener
    @return: Lista de objetos JSON
    """
    def obtener_coleccion_completa(self, nombre_coleccion, fecha_desde=None, fecha_hasta=None, limite=None):
        db = mongo_manager().get_db()
        filtro = {}

        if fecha_desde and fecha_hasta:
            if isinstance(fecha_desde, str):
                fecha_desde = datetime.fromisoformat(fecha_desde)
            if isinstance(fecha_hasta, str):
                fecha_hasta = datetime.fromisoformat(fecha_hasta)
            filtro["fecha"] = {
                "$gte": fecha_desde,
                "$lte": fecha_hasta
            }
        consulta = db[nombre_coleccion].find(filtro)

        if limite:
            consulta = consulta.limit(limite)

        datos = list(consulta)

        for dato in datos:
            if "_id" in dato:
                dato["_id"] = str(dato["_id"])
        
        return datos