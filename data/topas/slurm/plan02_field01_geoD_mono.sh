#!/bin/bash
#SBATCH --job-name=plan_2
#SBATCH --partition=q28,q36,qfat,q40,q48
#SBATCH --mem=2G
#SBATCH --ntasks=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=28
#SBATCH --time=04:00:00


echo "========= Job started  at `date` =========="


# Go to the directory where this job was submitted
cd $SLURM_SUBMIT_DIR
export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK:-1}

# set enviromental variables
export TOPAS_G4_DATA_DIR=$HOME/G4Data
export TopasDir=$HOME/tools/topascent/

# copy inputdata and the executable to the scratch-directory
mkdir -p /scratch/$SLURM_JOB_ID

cp -a $HOME/LETWorkshop/. /scratch/$SLURM_JOB_ID


# change directory to the local scratch-directory, and run:
cd /scratch/$SLURM_JOB_ID

$TopasDir/bin/topas data/topas/input/plan01_field01_geoC_SOBP74/main_160MeV.txt

# copy home the outputdata:
mkdir -p $SLURM_SUBMIT_DIR/Results
cp -r data/topas/results/output $SLURM_SUBMIT_DIR/Results/${SLURM_JOB_NAME}.$SLURM_JOB_ID

echo "========= Job finished at `date` =========="
#
