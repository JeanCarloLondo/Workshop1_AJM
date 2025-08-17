import argparse
import json
import random
from collections import defaultdict
from typing import Dict, List, Tuple

# ---------- Types ----------
Operation = Tuple[str, int]  # (job_id, op_index)
Schedule = Dict[Operation, Tuple[int, int]]  # (start, end)

# ---------- Default instance (replace if you want) ----------
DEFAULT_JOBS: Dict[str, List[Tuple[str, int]]] = {
    "J1": [("M3", 2), ("M2", 3), ("M1", 15)],
    "J2": [("M2", 4), ("M3", 2), ("M2", 6)],
    "J3": [("M1", 5), ("M2", 2), ("M3", 3)],
    "J4": [("M2", 2), ("M1", 8), ("M2", 2)],
    "J5": [("M3", 4), ("M1", 3), ("M1", 3)],
    "J6": [("M1", 6), ("M2", 5), ("M3", 2)]
}
MACHINES = ["M1", "M2", "M3"]  # M1=Oven, M2=Stove, M3=Blender

# ---------- Scheduling helpers ----------
def build_schedule(individual: List[Operation], jobs: Dict[str, List[Tuple[str, int]]]) -> Schedule:
    """Build a feasible schedule honoring job precedence and machine availability."""
    job_ready_time = defaultdict(int)
    machine_ready_time = defaultdict(int)
    schedule: Schedule = {}

    for (job, op_idx) in individual:
        machine, duration = jobs[job][op_idx]
        start_time = max(job_ready_time[job], machine_ready_time[machine])
        end_time = start_time + duration
        schedule[(job, op_idx)] = (start_time, end_time)
        job_ready_time[job] = end_time
        machine_ready_time[machine] = end_time
    return schedule

def makespan(schedule: Schedule) -> int:
    return max(end for (_, end) in schedule.values()) if schedule else 0

def sorted_schedule(schedule: Schedule):
    return sorted(schedule.items(), key=lambda x: x[1][0])

def compute_lb(jobs: Dict[str, List[Tuple[str, int]]]) -> Tuple[int, Dict[str, int], int]:
    """
    Lower bound (LB) = max( max machine load, longest job duration ).
    Returns (LB, load_by_machine, longest_job_duration).
    """
    machines = {m for ops in jobs.values() for (m, _) in ops}
    load_by_mach = {
        m: sum(d for ops in jobs.values() for (mm, d) in ops if mm == m)
        for m in machines
    }
    longest_job = max(sum(d for (_, d) in ops) for ops in jobs.values())
    lb = max(max(load_by_mach.values()), longest_job)
    return lb, load_by_mach, longest_job

# ---------- GA building blocks ----------
def generate_individual(jobs: Dict[str, List[Tuple[str, int]]]) -> List[Operation]:
    """
    Random precedence-feasible permutation by construction.
    We maintain a set of 'pending' next-ops for each job and sample among them.
    """
    ops: List[Operation] = []
    pending: List[Operation] = [(job, 0) for job in jobs]
    while pending:
        op = random.choice(pending)
        ops.append(op)
        pending.remove(op)
        job, idx = op
        if idx + 1 < len(jobs[job]):
            pending.append((job, idx + 1))
    return ops

def force_non_lb(ind: List[Operation], jobs: Dict[str, List[Tuple[str, int]]], lb: int, max_local: int = 400) -> List[Operation]:
    """
    If an individual's makespan equals the LB, try local random swaps to push it above LB.
    This guarantees initial population won't contain LB individuals (unless truly impossible).
    """
    def ms(x): return -fitness(x, jobs)
    if ms(ind) > lb:
        return ind
    tmp = ind[:]
    for _ in range(max_local):
        i, j = random.sample(range(len(tmp)), 2)
        tmp[i], tmp[j] = tmp[j], tmp[i]
        if ms(tmp) > lb:
            return tmp
    # If we couldn't push it above LB (pathological), return as-is.
    return tmp

def create_population_avoid_lb(size: int, jobs: Dict[str, List[Tuple[str, int]]], max_resamples: int = 500) -> List[List[Operation]]:
    """
    Create an initial population with NO individuals at the LB. If an individual hits LB,
    resample and/or locally perturb it to avoid LB.
    """
    lb, _, _ = compute_lb(jobs)
    pop: List[List[Operation]] = []
    for _ in range(size):
        tries = 0
        ind = generate_individual(jobs)
        while -fitness(ind, jobs) <= lb and tries < max_resamples:
            # First try pure resample a few times
            ind = generate_individual(jobs)
            tries += 1
        if -fitness(ind, jobs) <= lb:
            # Could still be LB -> force via local perturbation
            ind = force_non_lb(ind, jobs, lb)
        pop.append(ind)
    return pop

def fitness(individual: List[Operation], jobs: Dict[str, List[Tuple[str, int]]]) -> int:
    # GA maximizes; we want to minimize makespan
    return -makespan(build_schedule(individual, jobs))

def selection(population: List[List[Operation]], jobs: Dict[str, List[Tuple[str, int]]]) -> List[Operation]:
    """Tournament(2) selection."""
    a, b = random.sample(population, 2)
    return a if fitness(a, jobs) > fitness(b, jobs) else b

def crossover(p1: List[Operation], p2: List[Operation]) -> List[Operation]:
    """Slice from parent1, fill the rest with parent2 order (keeps uniqueness)."""
    size = len(p1)
    i, j = sorted(random.sample(range(size), 2))
    middle = p1[i:j]
    remaining = [op for op in p2 if op not in middle]
    return remaining[:i] + middle + remaining[i:]

def mutate(ind: List[Operation], prob: float = 0.2) -> List[Operation]:
    """Swap-mutation."""
    if random.random() < prob:
        i, j = random.sample(range(len(ind)), 2)
        ind[i], ind[j] = ind[j], ind[i]
    return ind