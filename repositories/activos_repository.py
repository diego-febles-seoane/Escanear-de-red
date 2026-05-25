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

    # ---- FILTROS DE BUSQUEDA DE LOS DISPOSITIVOS ACTIVOS ----
    """
    Metodo para buscar un activo por su dirección MAC
    @param mac: Dirección MAC a buscar
    @return: Objeto Activos encontrado o None si no se encuentra
    """
    def buscar_por_mac(self, mac):
        return self.collection.find_one({"mac": mac})
    
    """
    Metodo para buscar un activo por su dirección IP
    @param ip: Dirección IP a buscar
    @return: Objeto Activos encontrado o None si no se encuentra
    """
    def buscar_por_ip(self, ip):
        return self.collection.find_one({"ip": ip})

    """
    Metodo para buscar activos por su tipo de dispositivo
    @param tipo: Tipo de dispositivo a buscar
    @return: Lista de objetos Activos encontrados
    """
    def buscar_por_tipo(self, tipo):
        return self.collection.find({"tipo_dispositivo": tipo})

    """
    Metodo para buscar activos por su fabricante
    @param fabricante: Fabricante a buscar
    @return: Lista de objetos Activos encontrados
    """
    def buscar_por_fabricante(self, fabricante):
        return self.collection.find({"fabricante": fabricante})

    """
    Metodo para listar los activos más recientes en la base de datos
    @return: Lista de objetos Activos encontrados
    """
    def listar_recientes(self):
        return list(self.collection.find().sort("ultima_vez", -1))

    # ---- CONTADOR POR TIPO ----
    """
    Metodo para contar los activos por tipo de dispositivo
    @return: Lista de objetos Activos encontrados
    """
    def contar_por_tipo(self):
        pipeline = [
            {
                "$group": {
                    "_id":
                    "$tipo_dispositivo",
                    "total":
                    {
                        "$sum":
                        1
                    }
                }
            }
        ]
        return list(self.collection.aggregate(pipeline))

    """
    Metodo para contar los activos por fabricante
    @return: Lista de objetos Activos encontrados
    """
    def contar_por_fabricante(self):
        pipeline = [
            {
                "$group": {
                    "_id":
                    "$fabricante",
                    "total":
                    {
                        "$sum":
                        1
                    }
                }
            }
        ]
        return list(self.collection.aggregate(pipeline))

    """
    Metodo para contar los activos en la base de datos
    @return: Cantidad de activos en la base de datos
    """
    def total_activos(self):
        return self.collection.count_documents({})

    # ---- CONSULTAS DEL DASHBOARD ----
    """
    Metodo para obtener los datos del dashboard
    @return: Dicario con los datos del dashboard
    """
    def obtener_dashboard(self):
        return {
            "total_activos": self.total_activos(),
            "por_tipo": self.contar_por_tipo(),
            "por_fabricante": self.contar_por_fabricante(),
            "recientes": self.listar_recientes()
        }
