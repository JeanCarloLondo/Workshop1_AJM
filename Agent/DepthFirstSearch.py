# This is our secondary algorithm (DepthFS) used to make interesting comparisons and because we love to learn!

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

maxFrontierSize = 0 # Guarda el tamaño max de la pila cuando corre
foundPath = None  # Guarda la primera ruta que llegue a goal 

def dfs_puro(node, path, visited):
#nodo actual, lista con nodos visitados en la ruta actual. 
    global maxFrontierSize, foundPath

    currentFrontierSize = len(path)
    maxFrontierSize = max(maxFrontierSize, currentFrontierSize)

    if node == goal:
        foundPath = path[:]  #copia la ruta que llegó a path en foundPath
        return True  #Para la busqueda

    for neighbor in actions[node]:
        if neighbor not in visited:
            visited.add(neighbor)
            if dfs_puro(neighbor, path + [neighbor], visited):
                #nuevo nodo a visitar, la ruta acutal más el nuevo nodo, 
                return True 
            visited.remove(neighbor)
            #Si NO encontró el objetivo entonces hace backtracking, quita el vecino de 
            #visitados para que otro camino lo pueda visitar en un futuro.
            #Evita el bloqueo de rutas alternativas, puede que si yo me meto por otro lado
            #necesite B para pasar a otro estado que si lleve a goal.

    return False  # No hay solución bro



dfs_puro(initial, [initial], {initial}) #Recursividad tas tas tas


if foundPath:
    print("Ruta encontrada DFS puro:", foundPath)
else:
    print("No hay ruta bro .")

print(f"Size max de frontera: {maxFrontierSize}")