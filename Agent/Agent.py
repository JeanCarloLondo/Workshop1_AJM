import heapq
import time
from collections import deque

# ===== Problem definition =====
graph = {
    'Center': [('A',4), ('Est1',2)],
    'A': [('Center',4), ('B',6), ('C',3)],
    'B': [('A',6), ('Customer',5)],
    'C': [('A',3), ('Est1',2), ('Customer',2)],
    'Est1': [('Center',2), ('C',2)],
    'Customer': [('B',5), ('C',2)]
}

CHARGING = {'Est1', 'C'}  # Nodes where the drone can recharge
B_MAX = 10                # Maximum battery capacity
INITIAL = ('Center', B_MAX)
GOAL_LOC = 'Customer'

# ===== Utility functions =====
def is_goal(state):
    loc, _ = state
    return loc == GOAL_LOC

def actions(state):
    loc, battery = state
    acts = []
    # Move actions
    for nbr, w in graph.get(loc, []):
        if w <= battery:
            acts.append(('move', nbr, w))
    # Recharge action
    if loc in CHARGING and battery < B_MAX:
        acts.append(('recharge', loc, 0))
    return acts

def result(state, action):
    loc, battery = state
    typ, dest, cost = action
    if typ == 'move':
        return (dest, battery - cost)
    else:  # recharge
        return (loc, B_MAX)

def action_cost(action):
    return action[2]  # move cost or 0 for recharge

def reconstruct_path(node):
    path = []
    while node:
        path.append(node.state)
        node = node.parent
    return list(reversed(path))

# ===== UCS Implementation =====
class UCSNode:
    def __init__(self, state, parent=None, action=None, path_cost=0):
        self.state = state
        self.parent = parent
        self.action = action
        self.path_cost = path_cost
    def __lt__(self, other):
        return self.path_cost < other.path_cost
    
    def uniform_cost_search(initial_state, max_log=10):
      start_time = time.perf_counter()
      start = UCSNode(initial_state, path_cost=0)
      frontier = [(start.path_cost, start)]
      heapq.heapify(frontier)
      reached = {initial_state: start}
      nodes_expanded = 0
      max_frontier = 1
      expansion_log = []
      
      while frontier:
        _, node = heapq.heappop(frontier)
        if is_goal(node.state):
            runtime = time.perf_counter() - start_time
            return {
                'found': True,
                'path': reconstruct_path(node),
                'total_cost': node.path_cost,
                'nodes_expanded': nodes_expanded,
                'max_frontier': max_frontier,
                'runtime': runtime,
                'expansion_log': expansion_log
            }

        nodes_expanded += 1
        if len(expansion_log) < max_log:
            expansion_log.append(('UCS_expand', node.state, node.path_cost))

        for act in actions(node.state):
            child_state = result(node.state, act)
            step_cost = action_cost(act)
            child_cost = node.path_cost + step_cost
            child = UCSNode(child_state, node, act, child_cost)

            if (child_state not in reached) or (child_cost < reached[child_state].path_cost):
                reached[child_state] = child
                heapq.heappush(frontier, (child.path_cost, child))

        if len(frontier) > max_frontier:
            max_frontier = len(frontier)

      return {'found': False}