from datetime import datetime
from managers.mongo_manager import mongo_manager
from config.settings import COLLECTION_ALERTAS

"""
Clase para gestionar alertas
"""
class alertas_repository:

    """
    Constructor de la clase
    """
    def __init__(self):
        mongo = mongo_manager()
        db = mongo.get_db()
        self.collection = db[COLLECTION_ALERTAS]
    
    """
    Metodo para guardar una alerta en la base de datos
    @param tipo: Tipo de alerta
    @param mensaje: Mensaje de la alerta
    @param nivel: Nivel de la alerta (WARNING por defecto)
    @param mac: Dirección MAC del dispositivo (opcpcional)
    @param ip: Dirección IP del dispositivo (opcpcional)
    @return: Mensaje de confirmación o error
    """
    def guardar_alerta(self, tipo, mensaje, nivel="WARNING", mac=None, ip=None):
        alerta = {
            "fecha": datetime.now(),
            "tipo": tipo,
            "mensaje": mensaje,
            "nivel": nivel,
            "mac": mac,
            "ip": ip
        }
        self.collection.insert_one(alerta)
        return "Alerta guardada exitosamente"

    """
    Metodo para listar todas las alertas en la base de datos
    @return: Lista de alertas
    """
    def listar_todas(self):
        return list(self.collection.find().sort("fecha", -1))

    """
    Metodo para listar alertas por nivel
    @param nivel: Nivel de alerta a buscar
    @return: Lista de alertas
    """
    def listar_por_nivel(self, nivel):
        return list(self.collection.find({"nivel": nivel}).sort("fecha", -1))
    
    """
    Metodo para listar alertas por tipo
    @param tipo: Tipo de alerta a buscar
    @return: Lista de alertas
    """
    def listar_por_tipo(self, tipo):
        return list(self.collection.find({"tipo": tipo}).sort("fecha", -1))
    
    """
    Metodo para borrar todas las alertas en la base de datos
    @return: Resultado de la operación
    """
    def borrar_todas(self):
        return self.collection.delete_many({})