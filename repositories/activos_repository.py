from managers.mongo_manager import mongo_manager
from config.settings import COLLECTION_ACTIVOS

"""
Clase activos_repository para acceder a la colección activos en la base de datos
"""
class activos_repository:

    """
    Constructor de la clase activos_repository
    """
    def __init__(self):
        mongo = mongo_manager()
        db = mongo.get_db()
        self.collection = db["activos"]

    """
    Metodo para insertar varios activos en la base de datos
    @param documentos: Lista de objetos Activos a insertar
    """
    def insertar_muchos (self, documentos):
        datos = [
            d.to_dict()
            for d in documentos
        ]
        if datos:
            self.collection.insert_many(datos)

    """
    Metodo para borrar todos los activos en la base de datos
    """
    def borrar_todo(self):
        self.collection.delete_many({})
    
    """
    Metodo para listar todos los activos en la base de datos
    @return: Lista de objetos Activos
    """
    def listar_todos(self):
        return list(self.collection.find())
    
    """
    Metodo para contar los activos en la base de datos
    @return: Cantidad de activos en la base de datos
    """
    def contar(self):
        return self.collection.count_documents({})
    
