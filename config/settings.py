from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")
COLLECTION_HISTORIAL = os.getenv("COLLECTION_HISTORIAL")
COLLECTION_FABRICANTES = os.getenv("COLLECTION_FABRICANTES")
