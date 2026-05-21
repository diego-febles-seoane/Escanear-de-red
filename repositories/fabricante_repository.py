from datetime import datetime
from managers.mongo_manager import mongo_manager

"""
Repositorio de fabricantes de dispositivos
"""
class fabricnate_repository:

    """
    Clase para obtener información de fabricantes de dispositivos
    """
    def __init__(self):
        self.mongo = mongo_manager()
        self.db = self.mongo.get_db()
        self.collection = self.db["fabricantes"]

    """
    Busca un fabricante por su OUI
    @param oui: OUI del fabricante
    @return: Documento con la información del fabricante
    """
    def buscar_por_oui(self, oui):
        return self.collection.find_one({"oui": oui})

    """
    Inserta un nuevo fabricante en la base de datos
    @param oui: OUI del fabricante
    @param fabricante: Nombre del fabricante
    @return: Documento con la información del fabricante insertado
    """
    def insertar_fabricante(self, oui, fabricante):
        documento = {
            "oui": oui,
            "fabricante": fabricante,
            "creado_en": datetime.now()
        }
        self.collection.insert_one(documento)

        return documento