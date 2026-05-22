from services.scanner_service import scanner_service
from repositories.logs_repository import logs_repository

scanner = scanner_service()
scanner.escanar_y_guardar()

logs = logs_repository()
print("\nLOGS:\n")
for log in (logs.listar_todos()):
    print(log)