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