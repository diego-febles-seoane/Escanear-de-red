from services.export_service import export_service

exportador = export_service()

datos = exportador.obtener_coleccion_completa(
    "historial",
    limite=1000
)
exportador.exportar_excel(datos, "resultado.xlsx")

print("Exportación completada")