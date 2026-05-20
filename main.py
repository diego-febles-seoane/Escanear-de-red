from services.scanner_service import scanner_service

scanner = scanner_service()

ids = scanner.escanar_y_guardar()

print("\nIDs insertado:", ids)
