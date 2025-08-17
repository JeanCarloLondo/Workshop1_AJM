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
    
# ---------- Diagnostics ----------
def population_stats(population: List[List[Operation]], jobs: Dict[str, List[Tuple[str, int]]]) -> Tuple[int, float, int]:
    values = [-fitness(ind, jobs) for ind in population]
    return (min(values), sum(values) / len(values), max(values))

# ---------- CSV / Plot / IO ----------
def print_schedule(schedule: Schedule, jobs: Dict[str, List[Tuple[str, int]]]) -> None:
    print("\nBest schedule found:")
    for (job, idx), (start, end) in sorted_schedule(schedule):
        machine = jobs[job][idx][0]
        print(f"{job} Op{idx + 1} on {machine}: {start} → {end}")
    print(f"\nTotal makespan: {makespan(schedule)}")

def export_csv(schedule: Schedule, jobs: Dict[str, List[Tuple[str, int]]], path: str) -> None:
    import csv, os
    rows = []
    for (job, idx), (start, end) in sorted_schedule(schedule):
        machine, duration = jobs[job][idx]
        rows.append({
            "job": job,
            "op_index": idx + 1,
            "machine": machine,
            "duration": duration,
            "start": start,
            "end": end
        })
    os.makedirs(os.path.dirname(path), exist_ok=True) if os.path.dirname(path) else None
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"CSV saved to: {path}")

def plot_gantt(schedule: Schedule, jobs: Dict[str, List[Tuple[str, int]]], path: str) -> None:
    try:
        import matplotlib.pyplot as plt
    except Exception as e:
        print(f"Could not import matplotlib: {e}")
        return
    tasks = sorted_schedule(schedule)
    fig, ax = plt.subplots(figsize=(10, max(4, len(tasks) * 0.3)))
    machine_bands = {}
    for (job, idx), (start, end) in tasks:
        machine = jobs[job][idx][0]
        if machine not in machine_bands:
            machine_bands[machine] = len(machine_bands)
        band = machine_bands[machine]
        ax.barh(y=band, width=end - start, left=start)
        ax.text(start + (end - start) / 2, band, f"{job}-Op{idx+1}", ha="center", va="center", fontsize=8)
    ax.set_xlabel("Time")
    ax.set_ylabel("Machine")
    inv_map = {v: k for k, v in machine_bands.items()}
    ax.set_yticks(range(len(inv_map)))
    ax.set_yticklabels([inv_map[i] for i in range(len(inv_map))])
    ax.set_title("Gantt – Best schedule")
    ax.grid(True, axis="x", linestyle="--", alpha=0.4)
    fig.tight_layout()
    import os
    os.makedirs(os.path.dirname(path), exist_ok=True) if os.path.dirname(path) else None
    plt.savefig(path, dpi=150)
    plt.close(fig)
    print(f"Gantt saved to: {path}")

def load_jobs_from_file(path: str) -> Dict[str, List[Tuple[str, int]]]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    jobs: Dict[str, List[Tuple[str, int]]] = {}
    for job, ops in data.items():
        jobs[job] = [(str(m), int(d)) for (m, d) in ops]
    return jobs

# ---------- GA loop ----------
def evolve(population: List[List[Operation]],
           jobs: Dict[str, List[Tuple[str, int]]],
           generations: int = 150,
           mutation_prob: float = 0.2,
           elitism: bool = True,
           print_every: int = 15) -> List[Operation]:
    """Run the GA; returns the best individual found."""
    # Global best from initial population (already LB-free)
    best = max(population, key=lambda ind: fitness(ind, jobs))
    best_ms = -fitness(best, jobs)

    # Print LB & initial stats
    lb, loads, longest_job = compute_lb(jobs)
    pop_best, pop_avg, pop_worst = population_stats(population, jobs)
    print(f"Gen    0 | Gen-best: {pop_best} | Avg: {pop_avg:.2f} | Global-best: {best_ms} "
          f"(LB={lb}, loads={loads}, longest_job={longest_job})")

    # Evolution
    for gen in range(1, generations + 1):
        new_pop: List[List[Operation]] = []
        if elitism:
            new_pop.append(best[:])  # keep global best

        while len(new_pop) < len(population):
            p1 = selection(population, jobs)
            p2 = selection(population, jobs)
            child = crossover(p1, p2)
            child = mutate(child, mutation_prob)
            new_pop.append(child)

        population = new_pop[:len(population)]

        curr_best = max(population, key=lambda ind: fitness(ind, jobs))
        if fitness(curr_best, jobs) > fitness(best, jobs):
            best = curr_best

        gen_best_ms = -fitness(curr_best, jobs)
        glob_best_ms = -fitness(best, jobs)
        _, gen_avg, _ = population_stats(population, jobs)

        if (gen % max(1, print_every) == 0) or gen == 1 or gen == generations:
            print(f"Gen {gen:5d} | Gen-best: {gen_best_ms} | Avg: {gen_avg:.2f} | Global-best: {glob_best_ms}")

    return best