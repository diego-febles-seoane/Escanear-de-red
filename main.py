from services.scanner_service import scanner_service

scanner = scanner_service()

resultado = scanner.escanar_y_guardar()
for r in resultado:
    print(r)