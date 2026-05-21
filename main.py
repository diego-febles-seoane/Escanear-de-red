import json
from repositories.historial_repository import historial_repository

repo = historial_repository()

datos = repo.listar_todos_limpio()

print (datos)

