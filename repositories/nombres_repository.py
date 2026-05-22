from managers.mongo_manager import mongo_manager
from config.settings import COLLECTION_NOMBRES
from repositories.historial_repository import historial_repository

"""
Repositorio para la colección de nombres en la base de datos
"""
class nombres_repository:

    """
    Constructor del repositorio de nombres en la base de datos
    """
    def __init__(self):
        mongo = mongo_manager()
        db = mongo.get_db()
        self.collection = db[COLLECTION_NOMBRES]

    """
    Metodo para guardar un nombre en la base de datos
    @param mac: Dirección MAC del dispositivo
    @param nombre: Nombre a guardar
    @return: Mensaje de confirmación o error
    """
    def guardar_nombre(self, mac, nombre):
        historial_repo = historial_repository()
        existe = historial_repo.buscar_por_mac(mac)
        if not existe:
            return "ERROR: La mac no existe dentro de la lista. Asegurate de que sea correcta"
        
        nombre_existente = self.buscar_por_mac(mac)
        if nombre_existente:
            nombre_actual = nombre_existente.get("nombre")
            if nombre_actual != nombre:
                return (
                    "La MAC ya está asociada"
                    f"a '{nombre_actual}' "
                    "Usa actualizar_nombre() "
                    "para actualizar el nombre."
                )
        resulstado = self.collection.update_one(
            {"mac": mac},
            {"$set": {"nombre": nombre}},
            upsert=True
        )
        if resulstado.modified_count or resulstado.upserted_id:
            return "Nombre guardado exitosamente"

        return "ERROR: El nombre no guardado"

    """
    Metodo para actualizar un nombre en la base de datos
    @param mac: Dirección MAC del dispositivo
    @param nombre_nuevo: Nuevo nombre a guardar
    @return: Mensaje de confirmación o error
    """
    def actualizar_nombre(self, mac, nombre_nuevo):
        resulstado = self.collection.update_one(
            {"mac": mac},
            {"$set": {"nombre": nombre_nuevo}},
            upsert=True
        )
        if resulstado.modified_count or resulstado.upserted_id:
            return "Nombre actualizado exitosamente"

        return "ERROR: El nombre no actualizado"

    """
    Metodo para buscar un nombre por su dirección MAC
    @param mac: Dirección MAC a buscar
    @return: Objeto Nombre encontrado o None si no se encuentra
    """
    def buscar_por_mac(self, mac):
        return self.collection.find_one({"mac": mac})
    
    """
    Metodo para listar todos los nombres en la base de datos
    @return: Lista de objetos Nombre
    """
    def listar_todos(self):
        return list(self.collection.find())
