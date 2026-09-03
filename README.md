# Abaqus Batch Submission Tool (Linux / SLURM)

Automation script written in Python to streamline the batch submission of Abaqus FEA simulation jobs on High-Performance Computing (HPC) clusters managed by SLURM.

## Key Features
- **Smart `.inp` Filtering:** Automatically ignores files referenced via `*INCLUDE` directives and submits only main loadcase files containing valid `*STEP` blocks.
- **Duplicate Prevention:** Tracks submitted jobs using a `jobs.csv` control file to prevent re-submitting active or completed simulations.
- **Execution Logging:** Generates individual submission log files for each job in a designated `logs_submit/` directory.
- **Regex Extraction:** Automatically captures `SLURM_JOBID` from cluster response for easy monitoring.

## Usage
Place the script in the working directory containing your Abaqus input files (`.inp`) and run:

```bash
python batch_submit_abaqus.py

## Requirements
- Python 3.x
- Standard Python libraries (pathlib, subprocess, re, csv, os)
- Access to a Linux HPC environment with Abaqus/SLURM scheduler

_Author: Ana Beatriz Ataide | Mechanical Engineer & CAE Analyst_
