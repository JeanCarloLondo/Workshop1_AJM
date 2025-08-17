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