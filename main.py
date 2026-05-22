from repositories.logs_repository import logs_repository

repo = logs_repository()

print(repo.log_escaneo_parcial(5))
print(repo.log_escaneo_completo(14))
print(repo.log_dispositivo_nuevo("AA-BB-CC", "192.168.1.100"))
