from managers.mongo_manager import mongo_manager
from datetime import datetime

class query_builder_Service:

    """
    Obtiene los campos disponibles en la consulta
    @return: Lista de campos disponibles
    """
    def obtener_campos_disponibles(self):
        return [
            # ---- HISTORIAL ----
            { "label": "IP", "campo": "historial.ip", "tipo_input": "text" },
            { "label": "MAC", "campo": "historial.mac", "tipo_input": "text" },
            { "label": "Fecha", "campo": "historial.fecha", "tipo_input": "date" },
            { "label": "Fabricante", "campo": "historial.fabricante", "tipo_input": "text" },
            { "label": "Tipo dispositivo", "campo": "historial.tipo_dispositivo", "tipo_input": "text" },
            { "label": "Ubicación", "campo": "historial.ubicacion", "tipo_input": "text" },
            { "label": "Veces visto", "campo": "historial.veces_visto", "tipo_input": "number" },
            { "label": "Host Name", "campo": "historial.host_name", "tipo_input": "text" },
            { "label": "Nombre Red", "campo": "historial.nombre_red", "tipo_input": "text" },
            { "label": "Gateway IP", "campo": "historial.gateway_ip", "tipo_input": "text" },
            { "label": "Riesgo", "campo": "historial.riesgo", "tipo_input": "text" },
            { "label": "Nombre Dispositivo", "campo": "historial.nombre_dispositivo", "tipo_input": "text" },
            { "label": "Puertos", "campo": "historial.puertos", "tipo_input": "text" },
            { "label": "Primera Vez", "campo": "historial.primera_vez", "tipo_input": "date" },
            { "label": "Última Vez", "campo": "historial.ultima_vez", "tipo_input": "date" },
            # ---- NOMBRES ----
            { "label": "Nombre Personalizado", "campo": "nombres.nombre", "tipo_input": "text" },
            # ---- LOGS ----
            { "label": "Acción Log", "campo": "logs.accion", "tipo_input": "select" },
            { "label": "Nivel Log", "campo": "logs.nivel", "tipo_input": "select" },
            { "label": "Detalle Log", "campo": "logs.detalle", "tipo_input": "text" },
            { "label": "Fecha Log", "campo": "logs.fecha_log", "tipo_input": "date" }
        ]

    """
    Obtiene los campos usados en la consulta
    @param campos: Lista de campos a incluir en el resultado
    @param filtros: Lista de filtros a aplicar en la consulta
    @return: Lista de colecciones usadas en la consulta
    """
    def opbtener_campos_usadas(self, campos, filtros=None):
        colecciones = set()

        for campo in campos:
            colecciones.add(campo.split(".")[0])
        
        filtros = filtros or []

        for filtro in filtros:
            if "campo" in filtro:
                colecciones.add(filtro["campo"].split(".")[0])
        
        return list(colecciones)

    """
    Genera los joins automáticos para la consulta
    @param coleccion_base: Colección base de la consulta
    @param colecciones_usadas: Lista de colecciones usadas en la consulta
    @return: Lista de joins a realizar en la consulta
    """
    def genera_joins_automaticos(self, coleccion_base, colecciones):
        joins = []
        for coleccion in colecciones:
            if coleccion == coleccion_base:
                continue
            
            # Mapeo de campos de unión
            campo_union = "mac"
            if coleccion == "logs":
                campo_union = "mac" # logs también usa mac

            joins.append({
                "coleccion": coleccion,
                "campo_local": "mac",
                "campo_externo": campo_union,
                "tipo": "inner" # Usar inner para asegurar que solo salgan si existen en ambas
            })
        return joins

    """
    Crea una consulta en base a los parámetros proporcionados
    @param coleccion_base: Colección base de la consulta
    @param campos: Lista de campos a incluir en el resultado
    @param joins: Lista de joins a realizar en la consulta
    @param filtros: Lista de filtros a aplicar en la consulta
    @param orden: Orden de la consulta
    @param limite: Limite de resultados a devolver
    @param distinct: Si devolver solo valores únicos
    @param modo_resultado: Modo de devolución de resultados
    @return: Consulta creada
    """
    def crear_consulta(self, coleccion_base, campos=None, joins=None, filtros=None, orden=None, limite=100, distinct=False, modo_resultado="tabla"):
        if joins is None:
            colecciones_usadas = self.opbtener_campos_usadas(
                campos or [],
                filtros or []
            )
            joins = self.genera_joins_automaticos(coleccion_base, colecciones_usadas)

        return {
            "coleccion_base": coleccion_base,
            "campos": campos or [],
            "joins": joins,
            "filtros": filtros or [],
            "orden": orden or {},
            "limite": limite,
            "distinct": distinct,
            "modo_resultado": modo_resultado
        }
    
    """
    Ejecuta la consulta en la base de datos
    @param consulta: Consulta a ejecutar
    @return: Resultado de la consulta
    """
    def ejecutar_consulta(self, consulta):
        db = mongo_manager().get_db()

        coleccion_base = consulta["coleccion_base"]
        collection = db[coleccion_base]

        pipeline = []

        for join in consulta["joins"]:
            pipeline.append({
                "$lookup": {
                    "from": join["coleccion"],
                    "localField": join["campo_local"],
                    "foreignField": join["campo_externo"],
                    "as": join["coleccion"]
                }
            })
            if join["tipo"] == "inner":
                pipeline.append({
                    "$unwind": f"${join['coleccion']}"
                })

        match = self.generar_match(
            consulta.get("filtros", [])
        )
        if match:
            pipeline.append(
                {
                    "$match": match
                }
            )
        sort = self.generar_sort(
            consulta.get("orden")
        )
        if sort:
            pipeline.append({
                "$sort": sort
            })
        limite = consulta.get("limite")
        if limite:
            pipeline.append({
                "$limit": limite
            })
        project = self.generar_peject(consulta["campos"])
        pipeline.append({
            "$project": project
        })
        resultado = list(collection.aggregate(pipeline))
        if consulta.get("distinct"):
            resultado = self.aplicar_distinc(resultado, consulta["campos"])

        return resultado

    """
    Genera el pipeline de MongoDB para la consulta
    @param campos: Lista de campos a incluir en el resultado
    @return: Pipeline de MongoDB
    """
    def generar_peject(self, campos):
        project = {
            "_id": 0
        }
        for campo in campos:
            partes = campo.split(".")

            coleccion = partes[0]
            nombre_campo = partes[1]

            alias = campo.replace(".", "_")

            if coleccion == "historial":
                project[alias] = f"${nombre_campo}"
            else:
                project[alias] = f"${coleccion}.{nombre_campo}"
        return project

    """
    Genera el pipeline de MongoDB para la consulta
    @param filtros: Lista de filtros a aplicar en la consulta
    @return: Pipeline de MongoDB
    """
    def generar_match(self, filtros):
        match = {}

        for filtro in filtros:
            campo = filtro.get("campo")
            operador = filtro.get("operador")
            valor = filtro.get("valor")

            if not campo or not operador:
                continue

            partes = campo.split(".")
            coleccion = partes [0]
            nombre_campo = partes[1]

            if coleccion == "historial":
                campo_mongo = nombre_campo
            else:
                campo_mongo = f"{coleccion}.{nombre_campo}"
            
            if operador == "igual":
                match[campo_mongo] = valor
            elif operador == "contiene":
                match[campo_mongo] = {
                    "$regex": valor,
                    "$options": "i"
                }
            elif operador == "mayor_que":
                match[campo_mongo] = {
                    "gt": valor
                }
            elif operador == "menor_que":
                match[campo_mongo] = {
                    "lt": valor
                }
            elif operador == "entre":
                desde = valor.get("desde")
                hasta = valor.get("hasta")

                if isinstance(desde, str):
                    desde = datetime.fromisoformat(desde)

                if isinstance(hasta, str):
                    hasta = datetime.fromisoformat(hasta)
                match[campo_mongo] = {
                    "$gte": desde,
                    "$lte": hasta
                }
        return match

    """
    Genera el pipeline de MongoDB para la consulta
    @param orden: Ordenación a aplicar en la consulta
    @return: Pipeline de MongoDB
    """
    def generar_sort(self, orden):
        if not orden:
            return None
        
        campo = orden.get("campo")
        direccion = orden.get("direccion")

        if not campo:
            return None
        
        partes = campo.split(".")

        coleccion = partes[0]
        nombre = partes[1]

        if coleccion == "historial":
            campo_mongo = nombre
        else:
            campo_mongo = f"{coleccion}.{nombre}"
        return {
            campo_mongo:
            -1 if direccion == "desc"
            else 1
        }

    """
    Aplica el filtro de distinc a los resultados
    @param resultado: Lista de resultados
    @param campos: Lista de campos a aplicar el distinc
    @return: Lista de resultados con el distinc aplicado
    """
    def aplicar_distinc(self, resultado, campos):
        vistos = set()
        unicos = []

        for fila in resultado:
            clave = tuple(
                fila.get(
                    campo.replace(".", "_")
                )
                for campo in campos
            )
            if clave not in vistos:
                vistos.add(clave)
                unicos.append(fila)
        return unicos