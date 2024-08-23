SLURM_TEMPLATE = """#!/bin/bash
#SBATCH --job-name={job_name}
#SBATCH --output={output_file}
#SBATCH --error={error_file}
#SBATCH --time={time}
#SBATCH --mem={mem}
#SBATCH --cpus-per-task={cpus_per_task}
#SBATCH --partition={partition}
#SBATCH --nodes={nodes}
#SBATCH --ntasks={ntasks}

{commands}
"""