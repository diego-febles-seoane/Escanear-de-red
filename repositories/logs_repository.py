from datetime import datetime
from managers.mongo_manager import mongo_manager
from config.settings import COLLECTION_LOGS

"""
Clase para manejar los registros de logs en la base de datos
"""
class logs_repository:
    """
    Constructor de la clase logs_repository
    """
    def __init__(self):
        mongo = mongo_manager()
        db = mongo.get_db()
        self.collection = db[COLLECTION_LOGS]

    # ---- GUARDAR REGISTRO ----
    """
    Metodo para guardar un registro en la base de datos
    @param accion: Acción realizada
    @param detalle: Detalle de la acción
    @param nivel: Nivel de registro (INFO, WARNING, ERROR)
    @return: Mensaje de confirmación
    """
    def guardar_log(self, accion, detalle, nivel):
        log = {
            "fecha": datetime.now(),
            "accion": accion,
            "detalle": detalle,
            "nivel": nivel
        }
        self.collection.insert_one(log)
        return "Log guardado exitosamente"
    
    # ---- DIFERENTES TIPOS DE LOGS ----
    """
    Metodo para guardar un registro de escaneo parcial
    @param total: Total de dispositivos detectados
    @return: Mensaje de confirmación
    """
    def log_escaneo_parcial(self, total):
        return self.guardar_log(
            "ESCANEO_PARCIAL",
            f"Escaneo parcial finalizado con {total} dispositivos detectados",
            "INFO"
        )
    
    """
    Metodo para guardar un registro de escaneo completo
    @param total: Total de dispositivos detectados
    @return: Mensaje de confirmación
    """
    def log_escaneo_completo(self, total):
        return self.guardar_log(
            "ESCANEO_COMPLETO",
            f"Escaneo completo finalizado con {total} dispositivos detectados",
            "INFO"
        )
    
    """
    Metodo para guardar un registro de dispositivo nuevo
    @param mac: Dirección MAC del dispositivo
    @param ip: Dirección IP del dispositivo
    @return: Mensaje de confirmación
    """
    def log_dispositivo_nuevo(self, mac, ip):
        return self.guardar_log(
            "DISPOSITIVO_NUEVO",
            f"Dispositivo nuevo detectado con dirección MAC: {mac} y dirección IP: {ip}",
            "INFO"
        )
    
    """
    Metodo para guardar un registro de nombre asignado
    @param mac: Dirección MAC del dispositivo
    @param nombre: Nombre asignado
    @return: Mensaje de confirmación
    """
    def log_nombre_asignado(self, mac, nombre):
        return self.guardar_log(
            "NOMBRE_ASIGNADO",
            f"Nombre asignado a dispositivo con dirección MAC: {mac} a nombre: {nombre}",
            "INFO"
        )
    
    """
    Metodo para guardar un registro de nombre actualizado
    @param mac: Dirección MAC del dispositivo
    @param nombre: Nombre actualizado
    @return: Mensaje de confirmación
    """
    def log_nombre_actualizado(self, mac, nombre):
        return self.guardar_log(
            "NOMBRE_ACTUALIZADO",
            f"Nombre actualizado a dispositivo con dirección MAC: {mac} a nombre: {nombre}",
            "INFO"
        )
    
    """
    Metodo para guardar un registro de error
    @param error: Detalle del error
    @return: Mensaje de confirmación
    """
    def log_error(self, error):
        return self.guardar_log(
            "ERROR",
            str(error),
            "ERROR"
        )
    
    # ---- LISTADO Y BORRADO DE LOGS ----
    """
    Metodo para listar todos los registros de la base de datos
    @return: Lista de objetos Log
    """
    def listar_todos(self):
        return list(self.collection.find().sort("fecha", -1))
    
    """
    Metodo para listar todos los registros de la base de datos por nivel
    @param nivel: Nivel de registro (INFO, WARNING, ERROR)
    @return: Lista de objetos Log
    """
    def listar_por_nivel(self, nivel):
        return list(self.collection.find({"nivel": nivel}).sort("fecha", -1))
    
    """
    Metodo para borrar todos los registros de la base de datos
    """
    def borrar_todos(self):
        self.collection.delete_many({})
