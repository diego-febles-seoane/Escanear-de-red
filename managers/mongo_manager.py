from pymongo import MongoClient
from config.settings import MONGO_URI, DATABASE_NAME
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from panel.views import get_mongo_session_data
except ImportError:
    get_mongo_session_data = lambda: {}

"""
Clase para gestionar la conexión con la base de datos MongoDB
"""
class mongo_manager: 
    
    """
    Clase para gestionar la conexión con la base de datos MongoDB
    """
    def __init__(self):
        session_data = get_mongo_session_data()
        if session_data and 'user' in session_data and 'password' in session_data and 'host' in session_data:
            mongo_uri = f"mongodb+srv://{session_data['user']}:{session_data['password']}@{session_data['host']}/?appName=Redes"
        else:
            mongo_uri = MONGO_URI
            
        self.client = MongoClient(mongo_uri)
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