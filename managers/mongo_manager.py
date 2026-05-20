from pymongo import MongoClient
from config.settings import MONGO_URI, DATABASE_NAME
"""
Clase para gestionar la conexión con la base de datos MongoDB
"""
class mongo_manager: 
    """
    Clase para gestionar la conexión con la base de datos MongoDB
    """
    def __init__(self):
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[DATABASE_NAME]

    """
    Obtiene la base de datos MongoDB
    """
    def get_db(self):
        return self.db

    """
    Prueba la conexión con la base de datos MongoDB
    """
    def probar_conexion(self):
        self.client.admin.command("ping")
        return True