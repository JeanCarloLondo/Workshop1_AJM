initial = 'Center'
goal = 'Customer'

actions = {
    'Center': ['A', 'Est1'],     
    'A': ['Center', 'B', 'C'],
    'B': ['A', 'Customer'],
    'C': ['A', 'Est1', 'Customer'],
    'Est1': ['Center', 'C'],
    'Customer': ['B', 'C'],
}

costs = {
    ('Center', 'A'): 4, ('A', 'Center'): 4,
    ('Center', 'Est1'): 2, ('Est1', 'Center'): 2,
    ('A', 'B'): 6, ('B', 'A'): 6,
    ('A', 'C'): 3, ('C', 'A'): 3,
    ('B', 'Customer'): 5, ('Customer', 'B'): 5,
    ('C', 'Customer'): 2, ('Customer', 'C'): 2,
    ('Est1', 'C'): 2, ('C', 'Est1'): 2
}

chargingStations = {'C', 'Est1'}
batCap = 10


routes = []

maxFrontierSize = 0 #Variable para mostrar el máximo tamaño de frontera

def dfs_paths(node, battery, path, cost, visited):
    global maxFrontierSize

    # Actualizar máximo tamaño de frontera (pila activa)
    current_frontier_size = len(path)
    maxFrontierSize = max(maxFrontierSize, current_frontier_size)

    # Recargar si estamos en estación
    if node in chargingStations:
        battery = batCap

    # Meta alcanzada
    if node == goal:
        routes.append((path[:], cost))
        return

    for neighbor in actions[node]:
        edge_cost = costs[(node, neighbor)]
        # Evitar ciclos
        if neighbor in visited:
            continue
        # Cortar si no hay batería suficiente
        if battery - edge_cost < 0:
            continue

        visited.add(neighbor)
        dfs_paths(neighbor, battery - edge_cost, path + [neighbor], cost + edge_cost, visited)
        visited.remove(neighbor)

# Ejecutar DFS
dfs_paths(initial, batCap, [initial], 0, {initial})

# Resultados
if routes:
    print("Rutas validas encontradas:")
    for r, c in routes:
        print(f"Ruta: {r}, Consumo: {c}")

    # Escoger la de menor consumo
    bestRoute = min(routes, key=lambda x: x[1])
    print("\nMejor ruta encontrada:")
    print(f"Ruta: {bestRoute[0]}, Consumo total: {bestRoute[1]}")
else:
    print("No se encontraron rutas válidas.")

# Métricas de búsqueda
print(f"Tamaño maximo de frontera: {maxFrontierSize}")
