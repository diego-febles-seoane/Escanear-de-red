# Escanear-de-red

## Descripción del Proyecto
**Escanear-de-red** es una herramienta avanzada de monitoreo y gestión de redes diseñada para proporcionar visibilidad completa sobre los dispositivos conectados a una infraestructura local. A diferencia de los escáneres de red tradicionales que pueden ser intrusivos, este proyecto se enfoca en la **observación pasiva**, utilizando técnicas que minimizan el impacto en el rendimiento de la red y evitan ser detectados como tráfico malicioso.

El objetivo principal es permitir a los administradores de red y profesionales de seguridad mantener un inventario actualizado de activos, identificar dispositivos no autorizados, evaluar riesgos de seguridad y visualizar la topología de la red de manera intuitiva.

## Objetivos Generales
- **Descubrimiento de Activos:** Identificar todos los dispositivos presentes en la red mediante el análisis de tablas ARP y conexiones activas.
- **Clasificación Inteligente:** Categorizar automáticamente los dispositivos (servidores, impresoras, móviles, firewalls, etc.) basándose en sus características técnicas y fabricantes.
- **Análisis de Riesgo:** Evaluar la postura de seguridad de cada dispositivo asignando un nivel de riesgo basado en sus servicios abiertos y metadatos.
- **Monitoreo Histórico:** Mantener un registro detallado de cuándo aparecen y desaparecen los dispositivos de la red.
- **Alertas Proactivas:** Notificar sobre cambios significativos o la aparición de nuevos dispositivos sospechosos.

## Características Principales
- **Escaneo Pasivo:** Utiliza la biblioteca `psutil` y el análisis de la caché ARP para descubrir dispositivos sin realizar barridos de ping (ICMP) masivos.
- **Gestión de Inventario:** Panel de control completo para ver detalles de cada dispositivo, incluyendo IP, MAC, fabricante, tipo y nivel de riesgo.
- **Visualización de Topología:** Generación de un mapa visual de la red para entender las conexiones y la jerarquía de los dispositivos.
- **Generación de Informes:** Exportación de datos y creación de reportes detallados en formato PDF para auditorías o documentación técnica.
- **Query Builder:** Herramienta avanzada para realizar consultas personalizadas sobre la base de datos de dispositivos.
- **Seguridad:** Sistema de login integrado que se conecta directamente con una instancia de MongoDB Atlas.

## Stack Tecnológico
- **Lenguaje:** Python 3.x
- **Framework Web:** Django (para el panel de administración y visualización)
- **Base de Datos:** MongoDB (almacenamiento de historial, logs y activos)
- **Bibliotecas de Red:**
  - `Scapy`: Para análisis profundo de paquetes y manipulación de red.
  - `psutil`: Para monitorear conexiones locales y procesos de red.
- **Frontend:** HTML5, CSS3, JavaScript (Dashboard interactivo).
- **Generación de Reportes:** `xhtml2pdf` y `openpyxl`.

## Estructura del Repositorio
- `app_django/` & `panel/`: Núcleo de la aplicación web Django.
- `managers/`: Lógica de bajo nivel para la interacción con la red y MongoDB.
- `services/`: Capa de servicios que implementa la lógica de negocio (escaneo, clasificación, riesgo, alertas).
- `repositories/`: Capa de acceso a datos para la persistencia en MongoDB.
- `models/`: Definiciones de los objetos de dominio (Historial, Logs, Nombres).
- `templates/`: Plantillas HTML para la interfaz de usuario.
