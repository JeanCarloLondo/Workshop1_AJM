# Workshop1_AJM
This repository contains the development of the first workshop for the Introduction to AI course - EAFIT University

# Autonomous Delivery Drone with Limited Battery Capacity

This project addresses the route planning problem for an autonomous delivery drone operating under battery constraints.
The drone must deliver a package from a Distribution Center to the Customer’s Location within a small city map. Each move between locations consumes a specific amount of battery, and some locations contain charging stations where the drone can fully recharge.

## The challenge is to find an optimal route that ensures:

- The drone never runs out of battery before reaching the goal.

- The total battery consumption is minimized.

## The environment is modeled as a weighted undirected graph:

- Nodes → Locations (intersections, charging stations, delivery points)

- Edges → Possible movements between locations, with weights representing energy consumption.

## The state includes:

- Current location

- Remaining battery

# Algorithms

## We implemented and compared two search algorithms:

Property | Uniform Cost Search (UCS) | Breadth-First Search (BFS)
-- | -- | --
Completeness | Yes – guarantees finding a solution if one exists. | Yes – guarantees finding a solution if one exists.
Optimality | Yes – always finds the least-cost path. | Only if all actions have the same cost.
Memory | High – keeps all frontier nodes in a priority queue. | High – keeps all frontier nodes in a FIFO queue.
Time | Can be high – expands nodes in increasing cost order, which may explore many nodes before reaching the goal. | Can be high – expands nodes in breadth without cost prioritization.

# Team Members

- Jean Carlo Londoño Ocampo

- Alejandro Garcés Ramírez

- María Acevedo

# Technologies Used

- Python 3 – Programming language.

- heapq – Priority queue for UCS implementation.

- collections.deque – Efficient FIFO queue for BFS.

- time – Runtime measurement for performance analysis.
