from managers.mongo_manager import mongo_manager
from bson import ObjectId
"""
Clase para la repositorio de historiales de red
"""
class historial_repository:
    """
    Constructor de la clase HistorialRepository
    """
    def __init__(self):
        mongo = mongo_manager()
        self.db = mongo.get_db()
        self.collection = self.db["historial"]
    """
    Metodo para insertar un historial de red en la base de datos
    @param historial: Objeto Historial a insertar
    @return: ID del nuevo documento insertado
    """
    def insertar(self, historial):
        resultado = self.collection.insert_one(historial.to_dict())
        return resultado.inserted_id
    """
    Metodo para insertar varios historiales de red en la base de datos
    @param historiales: Lista de objetos Historial a insertar
    @return: Lista de IDs de los documentos insertados
    """
    def insertar_muchos(self, historiales):
        documentos = [
            historial.to_dict() 
            for historial in historiales
        ]
        resultado = (
            self.collection.insert_many(documentos)
        )
        return resultado.inserted_ids
    """
    Metodo para listar todos los historiales de red en la base de datos
    @return: Lista de objetos Historial
    """
    def listar_todos(self):
        return list(self.collection.find())
    """
    Metodo para buscar un historial de red por su ID
    @param id: ID del historial a buscar
    @return: Objeto Historial encontrado o None si no se encuentra
    """
    def buscar_por_id(self, id):
        return self.collection.find_one({"_id": ObjectId(id)})
    """    Metodo para buscar un historial de red por su dirección IP
    @param ip: Dirección IP a buscar
    @return: Objeto Historial encontrado o None si no se encuentra
    """
    def buscar_por_ip(self, ip):
        return self.collection.find_one({"ip": ip})
    """
    Metodo para buscar un historial de red por su dirección MAC
    @param mac: Dirección MAC a buscar
    @return: Objeto Historial encontrado o None si no se encuentra
    """
    def buscar_por_mac(self, mac):
        return self.collection.find_one({"mac": mac})
    """
    Metodo para buscar un historial de red por su nombre de host
    @param host_name: Nombre de host a buscar
    @return: Objeto Historial encontrado o None si no se encuentra
    """
    def buscar_por_host_name(self, host_name):
        return self.collection.find_one({"host_name": host_name})
    """
    Metodo para buscar un historial de red por su dirección IP de gateway
    @param gateway_ip: Dirección IP de gateway a buscar
    @return: Objeto Historial encontrado o None si no se encuentra
    """
    def buscar_por_gateway_ip(self, gateway_ip):
        return self.collection.find_one({"gateway_ip": gateway_ip})
    """
    Metodo para buscar un historial de red por su estado
    @param estado: Estado a buscar
    @return: Objeto Historial encontrado o None si no se encuentra
    """
    def buscar_por_estado(self, estado):
        return self.collection.find_one({"estado": estado})
    """
    Metodo para buscar un historial de red por su fecha
    @param fecha: Fecha a buscar
    @return: Objeto Historial encontrado o None si no se encuentra
    """
    def buscar_por_fecha(self, fecha):
        return self.collection.find_one({"fecha": fecha})
    """
    Metodo para buscar un historial de red por su nombre de red
    @param nombre_red: Nombre de red a buscar
    @return: Objeto Historial encontrado o None si no se encuentra
    """
    def buscar_por_nombre_red(self, nombre_red):
        return self.collection.find_one({"nombre_red": nombre_red})
    """
    Metodo para buscar un historial de red por su ubicación
    @param ubicacion: Ubicación a buscar
    @return: Objeto Historial encontrado o None si no se encuentra
    """
    def buscar_por_ubicacion(self, ubicacion):
        return self.collection.find_one({"ubicacion": ubicacion})
    """
    Metodo para buscar un historial de red por su tipo de fabricante
    @param tipo_fabricante: Tipo de fabricante a buscar
    @return: Objeto Historial encontrado o None si no se encuentra
    """
    def buscar_por_tipo_fabricante(self, tipo_fabricante):
        return self.collection.find_one({"tipo_fabricante": tipo_fabricante})
    """
    Metodo para buscar un historial de red por su nombre de dispositivo
    @param nombre_dispositivo: Nombre de dispositivo a buscar
    @return: Objeto Historial encontrado o None si no se encuentra
    """
    def buscar_por_nombre_dispositivo(self, nombre_dispositivo):
        return self.collection.find_one({"nombre_dispositivo": nombre_dispositivo})
    """
    Metodo para buscar un historial de red por su primera conexión
    @param primera_conexion: Primera conexión a buscar
    @return: Objeto Historial encontrado o None si no se encuentra
    """
    def buscar_por_primera_conexion(self, primera_conexion):
        return self.collection.find_one({"primera_conexion": primera_conexion})
    """
    Metodo para buscar un historial de red por su última conexión
    @param ultima_conexion: Última conexión a buscar
    @return: Objeto Historial encontrado o None si no se encuentra
    """
    def buscar_por_ultima_conexion(self, ultima_conexion):
        return self.collection.find_one({"ultima_conexion": ultima_conexion})
    """
    Metodo para contar el número de historiales de red en la base de datos
    @return: Número de historiales de red
    """
    def contar(self):
        return self.collection.count_documents({})
    """
    Metodo para borrar un historial de red por su ID
    @param id: ID del historial a borrar
    @return: None
    """
    def borrar_por_id(self, id):
        self.collection.delete_one({"_id": ObjectId(id)})
    """
    Metodo para borrar todos los historiales de red en la base de datos
    @return: None
    """
    def borrar_todo(self):
        self.collection.delete_many({})

    """
    Metodo para convertir un documento de la base de datos a una representación limpia
    @param documento: Documento de la base de datos
    @return: Documento convertido
    """
    def convertir_documento(self, documento):
        documento["_id"] = str(documento["_id"])

        if "fecha" in documento:
            documento["fecha"] = str(documento["fecha"])
        if "primera_vez" in documento:
            documento["primera_vez"] = str(documento["primera_vez"])
        if "ultima_vez" in documento:
            documento["ultima_vez"] = str(documento["ultima_vez"])
        return documento

    """
    Metodo para listar todos los historiales de red en la base de datos de manera limpia
    @return: Lista de historiales de red convertidos
    """
    def listar_todos_limpio(self):
        documentos = list(
            self.collection.find()
        )

        return [self.convertir_documento(documento) for documento in documentos]


def __init__(sef):
mongo =MongoManager ()
