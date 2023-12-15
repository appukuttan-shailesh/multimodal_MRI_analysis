#!/bin/bash
#SBATCH -J mriqc_test_BRAINT
#SBATCH -p batch
#SBATCH --mail-type=ALL 			
#SBATCH --mail-user=andrea.bagante@univ-amu.fr	
#SBATCH --ntasks-per-node=1
#SBATCH --mem-per-cpu=10G
#SBATCH -t 01:00:00
#SBATCH -N 1					
#SBATCH -o ./output/test_1.out
#SBATCH -e ./output/test_1.err

# chargement des module
module purge
module load all
module load singularity

#User inputs:
bids_root_dir=/envau/work/brainets/bagante.a/BraINT/data
pushd $bids_root_dir
subj=004 #'004 005' $(ls -d sub*) --> if I use this remove '/sub-${subj}'
popd
nthreads=2
mem=10 #gb
container=singularity #docker or singularity

#Make mriqc directory and participant directory in derivatives folder
if [ ! -d $bids_root_dir/derivatives/mriqc ]; then
mkdir $bids_root_dir/derivatives/mriqc 
fi

#if [ ! -d $bids_root_dir/derivatives/mriqc /sub-${subj} ]; then
#mkdir $bids_root_dir/derivatives/mriqc /sub-${subj}
#fi

#Run mriqc 
echo ""
echo "Running mriqc on participant $s"
echo ""

if [ $container == singularity ]; then
  singularity run -B $bids_root_dir:/data,$bids_root_dir/derivatives/:/out /hpc/shared/apps/x86_64/softs/singularity_BIDSApps/mriqc_0.16.1.sif \
  /data /out/mriqc \
  participant group \
  --n_proc $nthreads \
#  --hmc-fsl \
#  --correct-slice-timing \
  --mem_gb $mem \
  --float32 \
  --ants-nthreads $nthreads \
  -w /out/temp_mriqc
else
  docker run -it --rm -v $bids_root_dir:/data:ro -v $bids_root_dir/derivatives/mriqc/sub-${subj}:/out \
  poldracklab/mriqc:0.15.1 /data /out \
  participant \
  --n_proc $nthreads \
  --hmc-fsl \
  --correct-slice-timing \
  --mem_gb $mem \
  --float32 \
  --ants-nthreads $nthreads \
  -w $bids_root_dir/derivatives/mriqc/sub-${subj}
fi
