# Memoria Técnica del Proyecto

# NetScanner - Sistema de descubrimiento, inventariado y análisis de red

## 1. Introducción

NetScanner es una aplicación web orientada al descubrimiento, inventariado, análisis y visualización de dispositivos conectados a una red local. El sistema ha sido diseñado con el objetivo de proporcionar una herramienta práctica para identificar activos de red, clasificarlos automáticamente, evaluar su nivel de riesgo, registrar su evolución histórica y ofrecer una representación visual clara del estado actual de la red.

El proyecto nace como una solución para centralizar en una única aplicación varias tareas que normalmente se realizan mediante herramientas independientes: escaneo de red, análisis de dispositivos, consulta de historial, generación de informes y visualización topológica. A través de una interfaz web desarrollada con Django, el usuario puede lanzar escaneos, consultar dispositivos activos, revisar registros históricos, ejecutar consultas personalizadas y exportar la información en diferentes formatos.

Una de las principales características del sistema es la separación entre el estado actual de la red y el histórico acumulado. Para ello, la aplicación utiliza dos conceptos diferenciados: la Topología Activa, que representa únicamente los dispositivos detectados en el último escaneo, y el Historial de Red, que conserva todos los registros recopilados a lo largo del tiempo.

El proyecto utiliza MongoDB como sistema de persistencia, Scapy como herramienta principal para el análisis de red y Django como framework web. La interfaz se ha diseñado con un enfoque visual moderno, incorporando tema claro y oscuro, tarjetas tipo glassmorphism, animaciones y una distribución orientada a facilitar la interpretación rápida de los datos.

---

## 2. Objetivos del proyecto

El objetivo principal del proyecto es desarrollar una plataforma capaz de detectar, registrar y visualizar dispositivos conectados a una red local, ofreciendo al usuario una visión clara tanto del estado actual como del comportamiento histórico de la red.

Entre los objetivos específicos destacan:

- Detectar dispositivos conectados a la red local.
- Obtener información relevante como IP, MAC, fabricante, nombre de host y puertos observados.
- Clasificar automáticamente los dispositivos según fabricante, puertos y nombre.
- Registrar cada detección en una base de datos histórica.
- Mantener una colección independiente con los activos del último escaneo.
- Permitir asignar nombres personalizados a dispositivos mediante su dirección MAC.
- Calcular niveles de riesgo asociados a cada dispositivo.
- Calcular niveles de confianza según la recurrencia de detección.
- Representar visualmente la topología activa de la red.
- Permitir consultas personalizadas sobre la información almacenada.
- Generar informes y exportaciones en PDF, CSV, JSON y Excel.
- Diferenciar las exportaciones de Topología Activa y del Historial de Red.
- Proporcionar una interfaz clara, moderna y usable.

---

## 3. Tecnologías utilizadas

### 3.1 Python

Python es el lenguaje principal del proyecto. Se ha utilizado por su amplia disponibilidad de librerías orientadas a redes, automatización, procesamiento de datos y desarrollo web.

En este proyecto Python se utiliza para ejecutar la lógica de escaneo, procesar dispositivos detectados, clasificar activos, calcular riesgos, gestionar consultas a MongoDB, generar exportaciones y servir la aplicación web mediante Django.

Python también facilita la separación de responsabilidades mediante módulos, clases de servicio y repositorios. Esto permite que el código esté organizado de forma clara y que cada componente tenga una responsabilidad específica dentro del flujo general de la aplicación.

### 3.2 Django

Django se utiliza como framework web principal. Su papel dentro del sistema consiste en proporcionar la estructura del proyecto, definir rutas, renderizar plantillas HTML, gestionar vistas y coordinar las diferentes operaciones de backend.

Django se encarga de gestionar las URL de la aplicación, renderizar las páginas principales, exponer endpoints JSON, gestionar formularios y peticiones POST, proteger vistas mediante sesión, servir las exportaciones y coordinar los servicios y repositorios.

Aunque la persistencia principal se realiza en MongoDB, Django sigue siendo útil para gestionar la estructura web, las sesiones, la autenticación de acceso y la organización general del proyecto.

### 3.3 MongoDB Atlas

MongoDB Atlas se utiliza como base de datos principal. La elección de MongoDB se debe a la naturaleza flexible de los datos de red. Cada dispositivo puede contener campos variables, listas de puertos, información de fabricante, fechas, métricas de confianza y otros atributos que no siempre siguen una estructura rígida.

El uso de una base de datos documental permite almacenar cada dispositivo como un documento JSON-like, facilitando la evolución del modelo de datos durante el desarrollo.

Las principales colecciones del sistema son:

- `activos`
- `historial`
- `nombres`
- `logs`
- `alertas`

Cada una cumple una función específica dentro del sistema.

### 3.4 Scapy

Scapy es la librería utilizada para el análisis y descubrimiento de red. Inicialmente se planteó el uso de TShark, pero debido a limitaciones de permisos, compatibilidad y restricciones del entorno, se optó por Scapy.

Scapy permite construir, enviar, recibir y analizar paquetes de red desde Python. En este proyecto se utiliza principalmente para obtener información de dispositivos presentes en la red local.

Scapy aporta flexibilidad, integración directa con Python y capacidad suficiente para realizar el descubrimiento necesario en el contexto del proyecto.

### 3.5 Npcap

Npcap es un componente necesario en Windows para permitir la captura y envío de paquetes de red. Scapy depende de Npcap para poder interactuar correctamente con la interfaz de red.

Durante la instalación se recomienda activar la opción:

```text
Install Npcap in WinPcap API-compatible Mode
```

Esto mejora la compatibilidad con herramientas y librerías que esperan una interfaz similar a WinPcap.

### 3.6 Tailwind CSS

Tailwind CSS se utiliza para la construcción visual de la interfaz. Permite aplicar estilos de forma rápida mediante clases utilitarias directamente en las plantillas HTML.

En el proyecto se utiliza para distribución de elementos, espaciados, colores, bordes, sombras, responsive design, tarjetas y botones.

### 3.7 JavaScript

JavaScript se utiliza en el frontend para dotar de dinamismo a la aplicación.

Sus principales responsabilidades son obtener datos mediante `fetch`, renderizar tablas dinámicas, actualizar gráficas, controlar paginación, gestionar tooltips, gestionar animaciones de escaneo, filtrar dispositivos y actualizar la Topología Activa sin recargar completamente la página.

---

## 4. Arquitectura general del sistema

La aplicación está organizada siguiendo una arquitectura por capas. Esta separación facilita el mantenimiento, la comprensión y la evolución futura del proyecto.

Las capas principales son:

1. Capa de presentación.
2. Capa de vistas.
3. Capa de servicios.
4. Capa de repositorios.
5. Capa de persistencia.

### 4.1 Capa de presentación

La capa de presentación está formada por las plantillas HTML, CSS y JavaScript. Su objetivo es mostrar la información al usuario y permitir la interacción con el sistema.

Las pantallas principales son Login, Topología Activa, Historial de Red, Inventario, Consulta personalizada y Alertas.

Cada pantalla está diseñada para resolver una necesidad concreta del usuario.

La Topología Activa actúa como vista principal porque concentra la mayor parte de la información operativa: dispositivos activos, grupos, riesgos, confianza, búsqueda, resumen y exportaciones del último escaneo.

### 4.2 Capa de vistas

La capa de vistas está implementada en `views.py`. Es la encargada de recibir las peticiones HTTP, preparar los datos necesarios y devolver una respuesta.

Existen dos tipos principales de vistas:

- Vistas que renderizan páginas HTML.
- Vistas que devuelven datos JSON o archivos exportados.

Por ejemplo, la vista de Topología Activa renderiza la plantilla HTML, mientras que el endpoint `get_activos` devuelve los dispositivos activos del último escaneo en formato JSON.

### 4.3 Capa de servicios

La capa de servicios contiene la lógica principal del sistema.

Entre los servicios más importantes se encuentran el servicio de escaneo, servicio de clasificación, servicio de riesgo, servicio de comparación, servicio de exportación y servicio de consultas personalizadas.

Esta capa evita que la lógica compleja quede mezclada dentro de las vistas, mejorando la organización general del proyecto.

### 4.4 Capa de repositorios

La capa de repositorios actúa como intermediaria entre la aplicación y MongoDB.

Cada repositorio encapsula las operaciones asociadas a una colección concreta. Por ejemplo, el repositorio de historial se encarga de insertar, listar y consultar registros históricos, mientras que el repositorio de activos gestiona únicamente la colección del último escaneo.

Esta separación facilita modificar la forma de acceso a datos sin afectar directamente a las vistas o a los servicios.

### 4.5 Capa de persistencia

La persistencia se realiza en MongoDB Atlas. El sistema utiliza colecciones documentales para almacenar la información de dispositivos, nombres personalizados, logs y alertas.

MongoDB resulta adecuado porque los documentos pueden contener estructuras flexibles. Por ejemplo, un dispositivo puede tener una lista de puertos detectados, fechas, información de fabricante, estado, riesgo y otros campos sin necesidad de definir una estructura relacional fija.

---

## 5. Base de datos

### 5.1 Colección `activos`

La colección `activos` almacena únicamente los dispositivos detectados en el último escaneo.

Esta colección representa el estado actual de la red. Antes o durante cada nuevo escaneo, la colección se actualiza para reflejar únicamente los dispositivos presentes en ese momento.

La Topología Activa se alimenta de esta colección. Por ese motivo, si un dispositivo no aparece en el último escaneo, no se muestra en el mapa de red aunque exista en el historial.

Campos habituales:

- `_id`
- `ip`
- `mac`
- `host_name`
- `fabricante`
- `tipo_dispositivo`
- `puertos`
- `riesgo`
- `nombre_dispositivo`
- `ubicacion`
- `fecha`
- `primera_vez`
- `ultima_vez`
- `veces_visto`

### 5.2 Colección `historial`

La colección `historial` conserva todos los registros detectados a lo largo del tiempo.

Cada escaneo añade o actualiza información relacionada con los dispositivos observados. Esta colección permite analizar la evolución de la red, consultar dispositivos que ya no están activos y generar informes históricos.

El Historial de Red utiliza esta colección para mostrar todos los registros acumulados.

### 5.3 Colección `nombres`

La colección `nombres` almacena nombres personalizados asignados por el usuario a una dirección MAC.

Esto permite que un dispositivo no dependa únicamente del nombre detectado automáticamente. Si el usuario identifica un equipo concreto, puede asignarle un nombre más claro y ese nombre se utilizará posteriormente en inventario, historial y topología.

Ejemplo:

```json
{
  "mac": "aa-bb-cc-dd-ee-ff",
  "nombre": "Portátil Alejandro"
}
```

### 5.4 Colección `logs`

La colección `logs` registra eventos internos del sistema.

Puede almacenar información como dispositivo nuevo detectado, cambios de IP, cambios de riesgo, eventos del escáner y acciones relevantes del sistema.

Los logs permiten auditar qué ha ocurrido en la aplicación.

### 5.5 Colección `alertas`

La colección `alertas` almacena avisos generados automáticamente por el sistema.

Las alertas pueden producirse por diferentes motivos, como aparición de un dispositivo nuevo, cambio de IP, cambio de riesgo, fabricante sospechoso o comportamiento inesperado.

---

## 6. Sistema de escaneo

El sistema de escaneo es uno de los componentes centrales del proyecto.

Su objetivo es identificar dispositivos presentes en la red, recopilar información sobre ellos, clasificarlos, calcular su riesgo y guardar los resultados tanto en activos como en historial.

### 6.1 Funcionamiento general

Durante un escaneo, el sistema obtiene información de red, detecta dispositivos y construye un objeto por cada activo encontrado.

Cada dispositivo detectado pasa por varias fases:

1. Obtención de IP y MAC.
2. Resolución de fabricante.
3. Obtención de nombre de host si está disponible.
4. Análisis de puertos o conexiones observadas.
5. Clasificación de tipo de dispositivo.
6. Cálculo de riesgo.
7. Comprobación de nombre personalizado.
8. Cálculo de primera y última vez visto.
9. Actualización de contador de apariciones.
10. Guardado en historial y activos.

### 6.2 Uso de Scapy

Scapy permite realizar operaciones de red desde Python. En el proyecto se utiliza para detectar dispositivos en la red local.

La decisión de utilizar Scapy se tomó después de descartar TShark por limitaciones del entorno. Aunque TShark es una herramienta muy potente, requiere permisos, instalación y acceso al sistema que no siempre son sencillos de garantizar.

Scapy, en cambio, ofrece una integración directa con Python y permite controlar mejor el flujo de ejecución dentro de la aplicación.

### 6.3 Progreso del escaneo

El sistema mantiene una estructura global de progreso que permite informar al frontend sobre el estado del escaneo.

Esta estructura incluye porcentaje actual, estado, mensaje descriptivo, tiempo de inicio y tiempo estimado restante.

El frontend consulta periódicamente el endpoint de estado para actualizar la barra de progreso o la animación de olas en Topología Activa.

Estados principales:

- `idle`
- `running`
- `finished`
- `error`
- `cancelled`

---

## 7. Clasificación de dispositivos

La clasificación automática permite convertir datos técnicos en categorías comprensibles.

El sistema no se limita a mostrar el fabricante detectado. También intenta determinar qué tipo de dispositivo es cada activo.

### 7.1 Criterios de clasificación

La clasificación se basa en tres fuentes principales:

- Fabricante.
- Puertos detectados.
- Nombre de host.

Por ejemplo:

- Si el nombre contiene `printer` o aparece el puerto `9100`, se clasifica como impresora.
- Si aparece el puerto `3389`, se asocia a Windows.
- Si aparece el puerto `22`, se asocia a SSH.
- Si el fabricante contiene Cisco, TP-Link, Ubiquiti, MikroTik, Netgear, Aruba, WNC o Wistron, se clasifica como dispositivo de red.
- Si el fabricante contiene Intel, Dell, Lenovo, Acer, Asus, HP o Hewlett Packard, se clasifica como ordenador.
- Si el fabricante contiene Dahua, Hikvision, Axis o similares, se clasifica como cámara o seguridad.

### 7.2 Fabricantes OEM

Algunos fabricantes no representan marcas finales reconocibles, sino fabricantes OEM. Un ejemplo es WNC Corporation.

WNC Corporation puede fabricar hardware para routers, puntos de acceso, repetidores, cámaras IP, dispositivos IoT o equipos de operador.

Por eso, el sistema no debe mostrar necesariamente un bloque separado para WNC, sino clasificarlo como infraestructura o dispositivo de red.

Este enfoque mejora la claridad visual porque el usuario final normalmente necesita saber qué función cumple el dispositivo más que conocer el fabricante OEM exacto.

### 7.3 Agrupación visual

Una vez clasificado el dispositivo, el frontend normaliza su grupo visual.

Ejemplos de grupos:

- Ordenadores.
- Cámaras / Seguridad.
- Red / Multicast.
- Infraestructura de Red.
- Fortinet.
- Desconocidos.

La agrupación reduce el ruido visual y hace que la Topología Activa sea más sencilla de interpretar.

---

## 8. Sistema de nombres personalizados

El sistema permite asignar un nombre personalizado a una dirección MAC.

Esto es especialmente útil cuando el nombre detectado automáticamente no es claro. Muchos dispositivos aparecen como `Desconocido`, con el fabricante como nombre, o con un identificador poco útil.

El usuario puede actualizar el nombre desde el inventario. Cuando esto ocurre, se actualizan la colección `nombres`, los registros correspondientes en `historial` y los registros correspondientes en `activos`.

De este modo, el nombre personalizado aparece posteriormente en la Topología Activa, el Historial de Red y el Inventario.

---

## 9. Sistema de confianza

El sistema de confianza permite distinguir dispositivos nuevos de dispositivos habituales.

Esta funcionalidad se basa en el número de veces que un dispositivo ha sido visto.

### 9.1 Niveles de confianza

El sistema utiliza tres niveles:

#### Nuevo

Se asigna a dispositivos con una única detección o muy pocas apariciones.

Representa activos que todavía no forman parte del comportamiento habitual conocido de la red.

#### Observado

Se asigna a dispositivos vistos entre 2 y 5 veces.

Indica que el dispositivo ha aparecido más de una vez, pero todavía no existe suficiente historial para considerarlo completamente habitual.

#### Conocido

Se asigna a dispositivos vistos más de 5 veces.

Representa dispositivos recurrentes y habituales dentro de la red.

### 9.2 Utilidad del sistema de confianza

El nivel de confianza ayuda al usuario a priorizar la atención.

Un dispositivo nuevo puede requerir revisión, especialmente si aparece fuera de un horario habitual o si pertenece a un fabricante desconocido.

Un dispositivo conocido, en cambio, puede considerarse parte esperada de la infraestructura, salvo que cambie su riesgo, IP o comportamiento.

### 9.3 Representación visual

En la interfaz, el nivel de confianza se muestra mediante etiquetas visuales:

- Nuevo.
- Observado.
- Conocido.

También se incluye una leyenda explicativa para que el usuario entienda el significado de cada nivel.

---

## 10. Sistema de riesgo

El sistema de riesgo evalúa cada dispositivo y le asigna un nivel.

Los niveles principales son:

- Bajo.
- Medio.
- Alto.

### 10.1 Criterios de riesgo

El riesgo puede depender de tipo de dispositivo, puertos detectados, fabricante, servicios observados y comportamiento respecto a escaneos anteriores.

Por ejemplo, un dispositivo desconocido con servicios sensibles podría tener un riesgo mayor que un ordenador habitual sin puertos relevantes.

### 10.2 Uso visual del riesgo

El riesgo se representa mediante colores:

- Verde para bajo.
- Amarillo o ámbar para medio.
- Rojo para alto.

En la Topología Activa se muestra mediante una barra inferior en cada dispositivo. En el tooltip y en el panel de detalle también se representa dentro de un contenedor destacado.

---

## 11. Topología Activa

La Topología Activa es la pantalla principal de la aplicación.

Su función es mostrar el estado actual de la red, basándose únicamente en los dispositivos del último escaneo.

### 11.1 Diferencia con el Historial de Red

La Topología Activa no muestra todos los dispositivos registrados históricamente. Solo muestra los activos detectados en el escaneo más reciente.

Esto permite que la vista represente una fotografía actual de la red.

Si un dispositivo estuvo presente en días anteriores pero no aparece en el último escaneo, permanecerá en el historial pero no en la topología activa.

### 11.2 Distribución tipo Tetris

Inicialmente se planteó una visualización basada en nodos y conexiones, pero este enfoque resultaba poco adecuado para el contenedor disponible. Los nodos tendían a distribuirse en círculo y ocupaban demasiado espacio.

Por este motivo se rediseñó la topología como una distribución de bloques tipo Tetris.

Cada grupo representa una categoría de dispositivos y dentro de cada grupo aparecen tarjetas más pequeñas correspondientes a dispositivos individuales.

Este enfoque mejora legibilidad, aprovechamiento del espacio, claridad visual, escalabilidad y agrupación lógica.

### 11.3 Grupos de dispositivos

Los grupos se generan automáticamente según los dispositivos detectados.

No están definidos de forma fija, sino que se calculan dinámicamente a partir de los tipos detectados en el escaneo.

Esto permite que la interfaz se adapte a redes diferentes sin necesidad de modificar manualmente la estructura visual.

### 11.4 Tarjetas de dispositivos

Cada dispositivo se muestra como una tarjeta.

La tarjeta incluye icono representativo, nombre del dispositivo, dirección IP, etiqueta de confianza y barra de riesgo.

Al hacer hover, aparece un tooltip con más información.

Al hacer click, se abre un panel lateral con detalles completos.

### 11.5 Tooltip de dispositivo

El tooltip proporciona información rápida sin necesidad de abrir el panel de detalle.

Incluye nombre, IP, MAC, fabricante, tipo, primera vez visto, última vez visto, nivel de confianza y nivel de riesgo.

Este componente mejora la navegación y permite revisar rápidamente dispositivos sin abandonar la vista principal.

### 11.6 Panel de detalle

El panel de detalle ofrece una visión más completa de un dispositivo concreto.

Incluye campos como IP, MAC, fabricante, tipo, veces visto, primera vez, última vez y riesgo.

Este panel está pensado para inspección individual.

### 11.7 Resumen de activos

La parte superior de la Topología Activa incluye un resumen con métricas clave.

Entre ellas:

- Total de dispositivos detectados.
- Total de categorías.
- Total de fabricantes.
- Dispositivos de alto riesgo.
- Dispositivos nuevos.
- Último escaneo.

Este resumen permite comprender rápidamente el estado global de la red.

### 11.8 Animación de escaneo

Durante el escaneo, la vista de topología se oculta progresivamente y aparece una animación de olas.

Esta animación representa visualmente el proceso de análisis de red.

Como referencia simbólica a TShark, herramienta inicialmente considerada durante el desarrollo, se añadió un tiburón animado que nada entre las olas.

Aunque es un elemento visual, también cumple una función de experiencia de usuario: comunica que el sistema está trabajando y evita que la interfaz parezca bloqueada.

---

## 12. Historial de Red

El Historial de Red muestra los registros acumulados de dispositivos detectados.

A diferencia de la Topología Activa, esta vista no representa solo el último escaneo. Su objetivo es ofrecer una visión temporal y acumulada.

### 12.1 Tabla de historial

La tabla muestra IP, MAC, nombre del dispositivo, fabricante, puertos, riesgo, veces visto y fecha.

Esta información permite revisar detecciones anteriores y analizar cambios a lo largo del tiempo.

### 12.2 Paginación

Para evitar sobrecargar la interfaz, los registros se muestran paginados.

Esto mejora el rendimiento y facilita la navegación cuando existen muchos registros en la base de datos.

### 12.3 Gráficas

El Historial de Red incluye gráficas sencillas para representar escaneos de los últimos días y distribución de niveles de riesgo.

Las barras se redondearon completamente para mantener coherencia visual con el resto de la interfaz.

### 12.4 Exportaciones históricas

Desde el Historial de Red, las exportaciones corresponden al histórico completo.

Esto permite generar informes o archivos con todos los datos almacenados, no solo con los dispositivos activos del último escaneo.

---

## 13. Inventario

El inventario permite visualizar una lista de direcciones MAC y nombres asociados.

Su objetivo es facilitar la gestión de nombres personalizados.

Desde esta pantalla, el usuario puede comprobar qué dispositivos existen y qué nombre tienen asignado.

El inventario está relacionado con la colección `nombres` y con los registros de historial y activos, ya que los nombres personalizados deben reflejarse en todo el sistema.

---

## 14. Consulta personalizada

El Constructor de Consultas permite al usuario realizar consultas dinámicas sobre los datos almacenados.

### 14.1 Selección de campos

Los campos disponibles se presentan como burbujas seleccionables.

El usuario puede elegir qué campos desea visualizar en el resultado.

Las burbujas cambian de estilo al seleccionarse, mostrando un fondo verde, texto oscuro y un brillo visual para mejorar la legibilidad.

### 14.2 Categorías de campos

Los campos se organizan por categorías:

- Historial de dispositivos.
- Nombres personalizados.
- Logs de sistema.

Esto permite construir consultas más comprensibles y evita mostrar todos los campos mezclados.

### 14.3 Filtros

El usuario puede filtrar por campos como IP, MAC, fabricante, tipo, ubicación o fecha.

También puede definir rangos de fecha mediante campos desde y hasta.

### 14.4 Ordenación y límite

El sistema permite ordenar resultados por campos concretos y limitar el número máximo de registros devueltos.

Esto evita consultas demasiado grandes y mejora la experiencia de uso.

### 14.5 Resultados

Los resultados se muestran en tarjetas paginadas.

Cada tarjeta representa un registro y muestra únicamente los campos seleccionados por el usuario.

Este enfoque es más flexible que una tabla fija, ya que la estructura del resultado depende de la consulta realizada.

---

## 15. Exportaciones

El sistema permite exportar información en varios formatos:

- PDF.
- CSV.
- JSON.
- Excel.

### 15.1 Exportación desde Topología Activa

Cuando el usuario exporta desde Topología Activa, el sistema exporta únicamente la colección `activos`.

Esto significa que el archivo generado contiene solo los dispositivos detectados en el último escaneo.

### 15.2 Exportación desde Historial de Red

Cuando el usuario exporta desde Historial de Red, el sistema exporta la colección `historial`.

Esto permite obtener informes completos con todos los registros acumulados.

### 15.3 Parámetro `scope`

Para diferenciar ambos comportamientos, las URLs de exportación utilizan un parámetro:

- `scope=activos`
- `scope=historial`

El backend interpreta este parámetro y selecciona el repositorio adecuado antes de generar el archivo.

---

## 16. Sistema de alertas

El sistema de alertas permite registrar eventos relevantes.

Ejemplos:

- Nuevo dispositivo detectado.
- Cambio de IP.
- Cambio de nivel de riesgo.
- Fabricante sospechoso.
- Dispositivo inesperado.

Las alertas proporcionan una capa adicional de supervisión y ayudan al usuario a identificar eventos que requieren atención.

---

## 17. Logs del sistema

Los logs registran eventos internos de la aplicación.

A diferencia de las alertas, los logs pueden incluir información más operativa o técnica.

Sirven para auditar acciones, depurar problemas, revisar comportamiento del escáner y mantener trazabilidad de eventos.

---

## 18. Seguridad

La aplicación incorpora varias medidas básicas de seguridad.

### 18.1 Sesión MongoDB

El usuario debe iniciar sesión introduciendo credenciales de MongoDB.

La aplicación valida la conexión antes de permitir el acceso.

Esto evita que se pueda utilizar la aplicación sin una conexión válida a la base de datos.

### 18.2 Protección CSRF

Las peticiones POST utilizan protección CSRF de Django.

Esto es especialmente importante en acciones como lanzar escaneo, ejecutar consultas y actualizar nombres.

### 18.3 Separación de responsabilidades

El acceso a datos se realiza mediante repositorios y no directamente desde las plantillas.

Esto reduce el acoplamiento y permite controlar mejor qué operaciones puede realizar cada parte del sistema.

---

## 19. Interfaz visual

La interfaz ha sido diseñada con un estilo moderno, oscuro y técnico.

### 19.1 Glassmorphism

El diseño utiliza tarjetas semitransparentes, bordes suaves, desenfoque y sombras.

Este estilo permite separar visualmente los componentes sin utilizar bloques demasiado pesados.

### 19.2 Tema claro y oscuro

El sistema permite cambiar entre tema claro y oscuro.

El tema se guarda en `localStorage`, de modo que la preferencia del usuario se mantiene entre sesiones.

### 19.3 Animaciones

Las animaciones se utilizan para mejorar la comprensión del estado del sistema.

Ejemplos:

- Fade entre escaneo y topología.
- Animación de olas durante escaneo.
- Movimiento del tiburón.
- Aparición progresiva de grupos y tarjetas.
- Barras de gráficas animadas.

---

## 20. Limitaciones actuales

Aunque el sistema es funcional, existen algunas limitaciones.

### 20.1 Dependencia de permisos de red

Scapy requiere permisos adecuados y Npcap instalado correctamente.

Si el entorno no permite captura o envío de paquetes, el escaneo puede fallar.

### 20.2 Identificación aproximada

La clasificación se basa en heurísticas.

Esto significa que algunos dispositivos pueden clasificarse de forma genérica o incorrecta si el fabricante no es claro o si no hay puertos representativos.

### 20.3 Nombres de host no siempre disponibles

Muchos dispositivos no publican nombre de host o no responden a mecanismos de resolución.

En esos casos, el sistema recurre al fabricante y al tipo detectado.

### 20.4 Fabricantes OEM

Algunos fabricantes, como WNC Corporation, no indican claramente el tipo real de dispositivo.

El sistema intenta agruparlos funcionalmente, pero puede haber casos ambiguos.

---

## 21. Mejoras futuras

El proyecto permite muchas ampliaciones.

Posibles mejoras:

- Integración real con TShark o Wireshark.
- Detección pasiva avanzada.
- Detección de anomalías basada en comportamiento.
- Panel de actividad de dispositivos.
- Alertas configurables por usuario.
- Filtros avanzados en Topología.
- Comparación entre escaneos.
- Exportaciones filtradas.
- Integración con sistemas SIEM.
- Identificación de sistemas operativos.
- Geolocalización interna por segmentos de red.
- Autenticación de usuarios más avanzada.
- Roles y permisos.

---

## 22. Conclusión

NetScanner es una herramienta completa de análisis e inventariado de red local.

El proyecto combina descubrimiento de dispositivos, clasificación automática, persistencia histórica, visualización activa, consultas personalizadas y exportaciones.

La separación entre Topología Activa e Historial de Red permite cubrir dos necesidades diferentes: conocer el estado actual de la red y analizar su evolución a lo largo del tiempo.

El uso de Django, MongoDB y Scapy proporciona una base flexible y extensible. Además, la interfaz visual facilita la interpretación de información técnica por parte del usuario.

El resultado es una aplicación funcional, ampliable y orientada tanto a la supervisión práctica como a la documentación técnica de una red local.
