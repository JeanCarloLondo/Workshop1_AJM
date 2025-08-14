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

maxFrontierSize = 0  # Variable to track the maximum frontier size (stack depth)

def dfs_paths(node, battery, path, cost, visited):
    global maxFrontierSize

    # Update the maximum frontier size (current active stack size)
    current_frontier_size = len(path)
    maxFrontierSize = max(maxFrontierSize, current_frontier_size)

    # Recharge if we are at a charging station
    if node in chargingStations:
        battery = batCap

    # Goal reached
    if node == goal:
        routes.append((path[:], cost))
        return

    for neighbor in actions[node]:
        edge_cost = costs[(node, neighbor)]
        
        # Avoid cycles
        if neighbor in visited:
            continue
        
        # Skip if there is not enough battery
        if battery - edge_cost < 0:
            continue

        visited.add(neighbor)
        dfs_paths(neighbor, battery - edge_cost, path + [neighbor], cost + edge_cost, visited)
        visited.remove(neighbor)

# Run DFS
dfs_paths(initial, batCap, [initial], 0, {initial})

# Results
if routes:
    print("Valid routes found:")
    for r, c in routes:
        print(f"Route: {r}, Consumption: {c}")

    # Choose the one with the lowest consumption
    bestRoute = min(routes, key=lambda x: x[1])
    print("\nBest route found:")
    print(f"Route: {bestRoute[0]}, Total consumption: {bestRoute[1]}")
else:
    print("No valid routes found.")

# Search metrics
print(f"Maximum frontier size: {maxFrontierSize}")