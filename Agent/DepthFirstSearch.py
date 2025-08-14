# This is our secondary algorithm (DepthFS) used to make interesting comparisons and because we love to learn!

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

maxFrontierSize = 0  # Stores the maximum stack size during execution
foundPath = None     # Stores the first route that reaches the goal

def dfs_pure(node, path, visited):
    # current node, list with visited nodes in the current path
    global maxFrontierSize, foundPath

    currentFrontierSize = len(path)
    maxFrontierSize = max(maxFrontierSize, currentFrontierSize)

    if node == goal:
        foundPath = path[:]  # copies the route that reached the goal into foundPath
        return True  # Stops the search

    for neighbor in actions[node]:
        if neighbor not in visited:
            visited.add(neighbor)
            if dfs_pure(neighbor, path + [neighbor], visited):
                # new node to visit, the current route plus the new node
                return True
            visited.remove(neighbor)
            # If the goal was NOT found, perform backtracking:
            # remove the neighbor from visited so that another path
            # can visit it in the future.
            # This prevents blocking alternative routes — if we go
            # another way, we might need 'B' to reach a goal state.

    return False  # No solution found

# Recursion goes brrr
dfs_pure(initial, [initial], {initial})

if foundPath:
    print("DFS pure route found:", foundPath)
else:
    print("No route found.")

print(f"Max frontier size: {maxFrontierSize}")