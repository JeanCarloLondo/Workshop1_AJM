# Command-Line Interface (Flags)

The script `GeneticAlgorithm.py` includes a **CLI** with the following arguments:

| Flag | Description | Default |
|------|-------------|---------|
| `--pop-size` | Number of individuals in the population | `40` |
| `--generations` | Number of generations to run | `150` |
| `--mutation` | Probability of applying a swap-mutation | `0.2` |
| `--seed` | Random seed for reproducibility | `None` (random each run) |
| `--elitism` | Carry the best individual to the next generation (flag, no value needed) | `False` |
| `--jobs-file` | Path to JSON file with jobs and operations (format: `{job: [[machine, duration], ...]}`) | Uses `DEFAULT_JOBS` if not provided |
| `--plot` or `--plot-gantt` | File path to save the **Gantt chart** (requires matplotlib) | `None` |
| `--csv` | File path to save the **schedule in CSV format** | `None` |
| `--print-every` | Frequency (in generations) to print progress statistics | `15` |

---

# Output Files

Depending on the flags, the program can generate the following outputs:

- **Console output**:  
  Shows GA progress (`Gen-best`, `Avg`, `Global-best`) and prints the **best schedule** with start/end times and makespan.  

- **CSV file** (if `--csv schedule.csv` is set):  
  - Example filename: `schedule.csv`  
  - Contains rows with:  
    - Job ID (`job`)  
    - Operation index (`op_index`)  
    - Machine (`machine`)  
    - Duration (`duration`)  
    - Start time (`start`)  
    - End time (`end`)  

- **Gantt chart** (if `--plot gantt.png` is set):  
  - Example filename: `gantt.png`  
  - Horizontal bars by machine showing when each job operation is scheduled.  

---

# Quick Start

1. Use the provided `jobs_kitchen_example.json` or create your own JSON.  
2. Run:

```bash
python3 GeneticAlgorithm.py --jobs-file jobs_kitchen_example.json \
    --pop-size 40 \
    --generations 150 \
    --mutation 0.2 \
    --seed 42 \
    --plot gantt.png \
    --csv schedule.csv