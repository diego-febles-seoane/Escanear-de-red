from services.scanner_service import scanner_service
from repositories.activos_repository import activos_repository

scanner = scanner_service()
scanner.escanar_y_guardar()
repo = activos_repository()

print("ACTIVOS: ")
for dispositivo in repo.listar_todos():
    print(
        dispositivo.get("ip"),
        dispositivo.get("nombre_dispositivo"),
        dispositivo.get("tipo_dispositivo")
    )
