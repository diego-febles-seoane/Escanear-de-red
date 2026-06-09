# Manual de Usuario - NetScanner
![Banner](imgs/banner_net_scanner.png)

## 1. Introducción

NetScanner es una aplicación web desarrollada para descubrir, inventariar y analizar dispositivos conectados a una red local. La herramienta permite ejecutar escaneos, visualizar los dispositivos activos, consultar el historial de detecciones, asignar nombres personalizados, generar consultas avanzadas y exportar información en distintos formatos.

La aplicación está pensada para facilitar la supervisión de una red local desde una interfaz web clara y visual. Su pantalla principal es la Topología Activa, donde se muestran los dispositivos detectados en el último escaneo agrupados por categoría. Además, dispone de una sección de Historial de Red donde se conservan los registros acumulados.

---

## 2. Requisitos previos

Antes de ejecutar el proyecto es necesario instalar:

- Windows 10 o superior.
- Python 3.13.
- Npcap.
- Acceso a MongoDB Atlas.
- Navegador web moderno.
- PowerShell o terminal compatible.

Se recomienda utilizar Python 3.13 porque durante el desarrollo se detectaron problemas con versiones más recientes como Python 3.14 en algunos equipos.

---

## 3. Instalación de Python

Descargar Python desde:

https://www.python.org/downloads/

Durante la instalación se recomienda marcar:

- Add python.exe to PATH.
- Install launcher for all users, si se dispone de permisos.
- pip.
- venv.

Al finalizar, pulsar:

- Disable path length limit.

Después de instalar, cerrar y volver a abrir PowerShell.

Comprobar:

```powershell
python --version
```

o:

```powershell
py -0p
```

Si aparece Python 3.13, la instalación es correcta.

---

## 4. Crear entorno virtual

Desde la carpeta raíz del proyecto:

```powershell
py -3.13 -m venv venv
```

Si el comando `py` no funciona, usar Python directamente:

```powershell
python -m venv venv
```

Si Python no está en PATH, usar la ruta completa del ejecutable.

Comprobar que se ha creado la carpeta:

```powershell
dir
```

Debe aparecer una carpeta llamada:

```text
venv
```

---

## 5. Activar entorno virtual

En PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

Si aparece un error indicando que la ejecución de scripts está deshabilitada:

```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Aceptar con:

```text
S
```

Después volver a activar:

```powershell
.\venv\Scripts\Activate.ps1
```

Cuando esté activo, debe aparecer:

```text
(venv)
```

al inicio de la terminal.

---

## 6. Instalar dependencias

Con el entorno virtual activo:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Si falta alguna dependencia, instalar manualmente:

```powershell
pip install django pymongo dnspython scapy pandas openpyxl xlsxwriter reportlab xhtml2pdf
```

Comprobar dependencias:

```powershell
pip list
```

---

## 7. Instalar Npcap

Npcap es necesario para que Scapy pueda interactuar correctamente con la red en Windows.

Descargar desde:

https://npcap.com

Durante la instalación marcar:

```text
Install Npcap in WinPcap API-compatible Mode
```

Después de instalar Npcap puede ser necesario reiniciar el equipo.

---

## 8. Configuración del archivo .env

El proyecto utiliza un archivo `.env` para almacenar parámetros de configuración.

Ejemplo:

```env
MONGO_URI=mongodb+srv://usuario:password@host.mongodb.net/?appName=Redes
DATABASE_NAME=nombre_base_datos
```

La aplicación también permite introducir credenciales de MongoDB desde la pantalla de login.

---

## 9. Migraciones de Django

Aunque la información principal del proyecto se almacena en MongoDB, Django puede requerir sus tablas internas para sesiones, autenticación y administración.

Ejecutar:

```powershell
python manage.py migrate
```

---

## 10. Ejecutar la aplicación

Desde la raíz del proyecto y con el entorno activo:

```powershell
python manage.py runserver
```

Acceder desde el navegador:

```text
http://127.0.0.1:8000/
```

o:

```text
http://127.0.0.1:8000/panel/
```

---

## 11. Inicio de sesión
![Inicio de sesión](imgs/inicio_sesion.png)

Al abrir la aplicación se solicitarán credenciales de MongoDB:

- Usuario.
- Contraseña.
- Host de MongoDB Atlas.

La aplicación valida la conexión antes de permitir el acceso.


---

## 12. Topología Activa

La Topología Activa es la pantalla principal del sistema.

Muestra únicamente los dispositivos detectados en el último escaneo.

**Incluye:**

![Gráficas Topología](imgs/graficas_topologia.png)

- Resumen de activos.
- Tipos de dispositivo.
- Top fabricantes.
- Niveles de riesgo.
- Mapa de red por bloques.
- Leyenda de categorías.
- Nivel de confianza.
- Búsqueda de dispositivos.
- Panel de detalle.
- Tooltip al pasar el ratón.
- Exportaciones del último escaneo.

Los dispositivos se agrupan automáticamente por tipo. Cada tarjeta muestra nombre, IP, confianza y nivel de riesgo.

---

## 13. Escaneo de red

Para lanzar un escaneo, pulsar el botón:

```text
Actualizar topología
```
![Escaneo](imgs/topologia_en_proceso.png)

Durante el proceso se muestra una animación con olas y un tiburón como referencia visual a TShark, herramienta inicialmente considerada durante el desarrollo.

Al finalizar el escaneo:

- Se actualiza la colección `activos`.
- Se actualiza la colección `historial`.
- Se recalculan estadísticas.
- Se redibuja la topología.

---

## 14. Historial de Red

El Historial de Red muestra todos los registros acumulados.

**Incluye:**

- Tabla paginada.
- IP.
- MAC.
- Nombre del dispositivo.
- Fabricante.
- Puertos.
- Riesgo.
- Veces visto.
- Fecha.
- Gráficas de escaneos recientes.
- Gráficas de riesgo.

A diferencia de Topología Activa, esta sección no muestra solo el último escaneo, sino el histórico completo.

---

## 15. Inventario

El Inventario permite consultar direcciones MAC y nombres de dispositivos.

Sirve para identificar dispositivos y mantener nombres personalizados asociados a cada MAC.

Si se modifica el nombre de un dispositivo, este cambio se refleja en:

- Inventario.
- Historial.
- Topología Activa.
- Colección de nombres personalizados.

---

## 16. Consulta personalizada

El Constructor de Consultas permite realizar búsquedas avanzadas.

![Consulta](imgs/query_personalizada.png)

**Funciones:**

- Seleccionar campos.
- Filtrar por IP, MAC, fabricante, tipo, ubicación o fecha.
- Filtrar por rango de fechas.
- Ordenar resultados.
- Limitar número de registros.
- Ver resultados paginados.

Los campos seleccionados aparecen como burbujas activas con fondo verde, texto oscuro y efecto glow.

---

## 17. Alertas

La sección de alertas muestra eventos relevantes detectados por el sistema.

Ejemplos:

- Dispositivo nuevo.
- Cambio de IP.
- Cambio de riesgo.
- Fabricante sospechoso.
- Actividad relevante.



---

## 18. Exportaciones

La aplicación permite exportar datos en:

![Exportadores](imgs/exportadores.png)

- PDF.
- CSV.
- JSON.
- Excel.

El comportamiento depende de la sección:

### Desde Topología Activa

Exporta únicamente los dispositivos activos del último escaneo.

Usa:

```text
scope=activos
```

### Desde Historial de Red

Exporta el historial completo.

Usa:

```text
scope=historial
```

---

## 19. Tema claro y oscuro

La aplicación incluye botón flotante para alternar entre modo claro y modo oscuro.

La preferencia se guarda en `localStorage`.

---

## 20. Solución de problemas

### Python no se reconoce

Comprobar instalación y PATH:

```powershell
python --version
py -0p
```

Si no aparece, reinstalar Python 3.13 desde python.org y marcar `Add python.exe to PATH`.

### Pip no funciona

Ejecutar:

```powershell
python -m ensurepip --upgrade
python -m pip install --upgrade pip
```

### Error con xhtml2pdf

Instalar:

```powershell
pip install xhtml2pdf
```

### Error con pymongo

Instalar:

```powershell
pip install pymongo dnspython
```

### Error de Scapy

Instalar Npcap y reiniciar el equipo.

### Error de migraciones

Ejecutar:

```powershell
python manage.py migrate
```

### Error de MongoDB

Comprobar:

- Usuario.
- Contraseña.
- Host.
- IP permitida en MongoDB Atlas.
- Conectividad a Internet.