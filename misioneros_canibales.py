# ==========================================
# PROBLEMA DE LOS MISIONEROS Y CANIBALES
# ==========================================

from collections import deque
from time import perf_counter

# Estado inicial: todos estan en la izquierda
INICIO = (3, 3, 0)

# Estado objetivo: todos estan en la derecha
META = (0, 0, 1)

# Acciones posibles del bote: (misioneros, canibales)
ACCIONES = [(1, 0), (2, 0), (0, 1), (0, 2), (1, 1)]


# ==========================================
# VALIDACION DE ESTADOS
# ==========================================
def estado_valido(estado):
    misioneros_izq, canibales_izq, bote = estado
    if not (0 <= misioneros_izq <= 3):
        return False

    if not (0 <= canibales_izq <= 3):
        return False

    if bote not in (0, 1):
        return False

    misioneros_der = 3 - misioneros_izq
    canibales_der = 3 - canibales_izq

    # Seguridad en ambas orillas
    return not (
        (misioneros_izq > 0 and canibales_izq > misioneros_izq)
        or (misioneros_der > 0 and canibales_der > misioneros_der)
    )


# ==========================================
# GENERACION DE SUCESORES
# ==========================================
def generar_sucesores(estado):
    m, c, bote = estado
    sucesores = []

    for dm, dc in ACCIONES:
        if bote == 0:
            # El bote cruza de izquierda a derecha
            if dm > m or dc > c:
                continue

            nuevo_estado = (m - dm, c - dc, 1)
        else:
            # El bote cruza de derecha a izquierda
            if dm > (3 - m) or dc > (3 - c):
                continue

            nuevo_estado = (m + dm, c + dc, 0)

        if estado_valido(nuevo_estado):
            sucesores.append((nuevo_estado, (dm, dc)))

    return sucesores


# ==========================================
# BUSQUEDA BFS Y DFS
# ==========================================
def ejecutar_busqueda(inicio, meta, modo="BFS"):
    if modo not in ("BFS", "DFS"):
        raise ValueError("El modo debe ser BFS o DFS")

    tiempo_inicio = perf_counter()

    frontera = deque([inicio]) if modo == "BFS" else [inicio]

    visitados = {inicio}

    # Cada estado guarda su padre y la accion utilizada
    padres = {inicio: (None, None)}

    nodos_expandidos = 0
    nodos_generados = 1
    frontera_maxima = 1

    while frontera:
        if modo == "BFS":
            nodo_actual = frontera.popleft()
        else:
            nodo_actual = frontera.pop()

        if nodo_actual == meta:
            camino = []
            acciones_camino = []
            rastreador = meta

            while rastreador is not None:
                camino.append(rastreador)

                padre, accion = padres[rastreador]

                if accion is not None:
                    acciones_camino.append(accion)

                rastreador = padre

            camino.reverse()
            acciones_camino.reverse()

            tiempo_final = perf_counter() - tiempo_inicio

            return {
                "modo": modo,
                "camino": camino,
                "acciones": acciones_camino,
                "nodos_expandidos": nodos_expandidos,
                "nodos_generados": nodos_generados,
                "frontera_maxima": frontera_maxima,
                "tiempo": tiempo_final,
            }

        nodos_expandidos += 1

        for siguiente, accion in generar_sucesores(nodo_actual):
            if siguiente not in visitados:
                visitados.add(siguiente)

                padres[siguiente] = (nodo_actual, accion)

                frontera.append(siguiente)

                nodos_generados += 1

        frontera_maxima = max(frontera_maxima, len(frontera))

    tiempo_final = perf_counter() - tiempo_inicio

    return {
        "modo": modo,
        "camino": None,
        "acciones": [],
        "nodos_expandidos": nodos_expandidos,
        "nodos_generados": nodos_generados,
        "frontera_maxima": frontera_maxima,
        "tiempo": tiempo_final,
    }


# ==========================================
# DESCRIPCION DE LAS ACCIONES
# ==========================================
def descripcion_accion(estado, accion):
    dm, dc = accion
    if estado[2] == 0:
        direccion = "Izquierda -> Derecha"
    else:
        direccion = "Derecha -> Izquierda"

    partes = []

    if dm > 0:
        partes.append(f"{dm} misionero(s)")

    if dc > 0:
        partes.append(f"{dc} canibal(es)")

    pasajeros = " y ".join(partes)

    return f"{pasajeros}: {direccion}"


# ==========================================
# MOSTRAR RESULTADOS
# ==========================================
def mostrar_resultados(resultado):
    print("\n================================")
    print("ALGORITMO:", resultado["modo"])
    print("================================")

    if resultado["camino"] is None:
        print("No se encontro solucion.")
        return

    print("\nSecuencia de estados:")

    for i, estado in enumerate(resultado["camino"]):
        print(f"Paso {i}: {estado}")

    print("\nSecuencia de acciones:")

    for i, accion in enumerate(resultado["acciones"]):
        estado_actual = resultado["camino"][i]

        descripcion = descripcion_accion(estado_actual, accion)

        print(f"Cruce {i + 1}: {descripcion} {accion}")

    print("\nLongitud del camino:", len(resultado["camino"]) - 1)

    print("Nodos expandidos:", resultado["nodos_expandidos"])

    print("Nodos generados:", resultado["nodos_generados"])

    print("Frontera maxima:", resultado["frontera_maxima"])

    print("Tiempo de ejecucion:", f"{resultado['tiempo']:.8f} segundos")


# ==========================================
# BENCHMARK
# ==========================================
def ejecutar_benchmark(repeticiones=1000):
    if repeticiones <= 0:
        raise ValueError("Las repeticiones deben ser positivas")

    tiempos_bfs = []
    tiempos_dfs = []

    for _ in range(repeticiones):
        resultado_bfs = ejecutar_busqueda(INICIO, META, "BFS")

        tiempos_bfs.append(resultado_bfs["tiempo"])

        resultado_dfs = ejecutar_busqueda(INICIO, META, "DFS")

        tiempos_dfs.append(resultado_dfs["tiempo"])

    promedio_bfs = sum(tiempos_bfs) / repeticiones
    promedio_dfs = sum(tiempos_dfs) / repeticiones

    print("\n================================")
    print("RESULTADOS DEL BENCHMARK")
    print("================================")

    print("Numero de ejecuciones:", repeticiones)

    print("Tiempo promedio BFS:", f"{promedio_bfs:.8f} segundos")

    print("Tiempo promedio DFS:", f"{promedio_dfs:.8f} segundos")


# ==========================================
# FACTOR DE RAMIFICACION EFECTIVO
# ==========================================
def calcular_factor_ramificacion_efectivo(nodos_generados, profundidad):

    inferior = 0.0
    superior = float(nodos_generados)

    for _ in range(100):
        medio = (inferior + superior) / 2

        total = sum(medio**nivel for nivel in range(profundidad + 1))

        if total < nodos_generados:
            inferior = medio
        else:
            superior = medio

    return (inferior + superior) / 2


# ==========================================
# PROGRAMA PRINCIPAL
# ==========================================
if __name__ == "__main__":
    print("PROBLEMA DE MISIONEROS Y CANIBALES")

    print("\nEjecutando BFS...")

    resultado_bfs = ejecutar_busqueda(INICIO, META, "BFS")

    mostrar_resultados(resultado_bfs)

    print("\nEjecutando DFS...")

    resultado_dfs = ejecutar_busqueda(INICIO, META, "DFS")

    mostrar_resultados(resultado_dfs)

    ejecutar_benchmark(1000)

    if resultado_bfs["camino"] and resultado_dfs["camino"]:
        profundidad_bfs = len(resultado_bfs["camino"]) - 1
        profundidad_dfs = len(resultado_dfs["camino"]) - 1

        factor_bfs = calcular_factor_ramificacion_efectivo(
            resultado_bfs["nodos_generados"], profundidad_bfs
        )

        factor_dfs = calcular_factor_ramificacion_efectivo(
            resultado_dfs["nodos_generados"], profundidad_dfs
        )

        print("\n================================")
        print("FACTOR DE RAMIFICACION EFECTIVO")
        print("================================")

        print(f"BFS: {factor_bfs:.4f}")
        print(f"DFS: {factor_dfs:.4f}")
