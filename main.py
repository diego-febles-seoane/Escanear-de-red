from services.query_builder import query_builder_Service
from repositories.nombres_repository import nombres_repository

repo = nombres_repository()

query = query_builder_Service()

consulta1 = repo.guardar_nombre(
    "98-5f-41-61-79-7a",
    "Portátil Alejandro"
)
consulta = (
    query.crear_consulta(
        coleccion_base="historial",
        campos=[
            "historial.ip",
            "nombres.nombre"
        ]
    )
)
resultado = (
    query.ejecutar_consulta(consulta)
)
for r in resultado:
    print(r)