#!/bin/bash

#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH -c 16
#SBATCH --time=30:00:00
#SBATCH --mem=30GB
#SBATCH --gres=gpu:1
#SBATCH --job-name=whisperx

module purge

singularity exec --nv --overlay /scratch/map22-share/whisperx/whisperx.ext3:ro /scratch/work/public/singularity/cuda11.8.86-cudnn8.7-devel-ubuntu22.04.2.sif /bin/bash -c "

source /ext3/env.sh

cd /scratch/sb9179/datasets/

python -u run-parallel.py --input_dir /scratch/projects/pichenylab/sb9179/Rall/missing/missing_files/ --output_dir /scratch/projects/pichenylab/sb9179/Rall/missing/missing_files/outputs/  --language ja

"
