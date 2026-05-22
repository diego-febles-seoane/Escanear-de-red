from repositories.activos_repository import activos_repository

repo = activos_repository()

dashboard = repo.obtener_dashboard()
print("\nTOTAL ACTIVOS: ")
print(dashboard["total_activos"])
print("\nPOR TIPO: ")
print(dashboard["por_tipo"])
print("\nPOR FABRICANTE: ")
print(dashboard["por_fabricante"])
print("\nRECENTES: ")
for reciente in dashboard["recientes"]:
    print(reciente)
