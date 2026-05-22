from repositories.historial_repository import historial_repository

repo = historial_repository()

mac = "ff-ff-ff-ff-ff-ff"

ultimo = repo.buscar_ultimo_registro_por_mac(mac)

print(ultimo["_id"])
print(ultimo["ultima_vez"])
