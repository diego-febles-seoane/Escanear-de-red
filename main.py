import json
from repositories.historial_repository import historial_repository
from services.scanner_service import scanner_service

repo = historial_repository()

datos = repo.listar_todos_limpio()

scanner=scanner_service()

ids=scanner.escanar_y_guardar()

print (datos)

