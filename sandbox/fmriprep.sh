#!/bin/bash
#SBATCH -J fmriprep_test_BRAINT
#SBATCH -p batch
#SBATCH --mail-type=ALL 		
#SBATCH --mail-user=andrea.bagante@univ-amu.fr
#SBATCH --nodes=1					
#SBATCH --mem=92GB
#SBATCH --cpus-per-task=16
#SBATCH --time=50:00:00					
#SBATCH -o ./output/test_2.out
#SBATCH -e ./output/test_2.err


# chargement des module
module purge
module load all
module load singularity

#User inputs:
work=/envau/work/brainets/bagante.a/BraINT
bids_root_dir=/envau/work/brainets/bagante.a/BraINT/data
pushd $bids_root_dir
subj=010 #'004 005' $(ls -d sub*) --> if I use this remove '/sub-${subj}'
popd
nthreads=2
mem=48000 #gb
container=singularity #docker or singularity

#Make fmriprep directory and participant directory in derivatives folder
if [ ! -d $bids_root_dir/derivatives/fmriprep ]; then
mkdir $bids_root_dir/derivatives/fmriprep 
fi

#if [ ! -d $bids_root_dir/derivatives/fmriprep/sub-${subj} ]; then
#mkdir $bids_root_dir/derivatives/fmriprep/sub-${subj}
#fi

#Run fMRIprep
echo ""
echo "Running fMRIprep on participant $s"
echo ""

singularity run -B $bids_root_dir:/data,$bids_root_dir/derivatives/fmriprep/:/out,/envau/work/brainets/bagante.a/BraINT:/work /hpc/shared/apps/x86_64/softs/singularity_BIDSApps/fmriprep_21.0.2.sif \
--fs-license-file /work/license.txt /data /out \
participant --participant-label $subj \
--mem $mem \
--clean-workdir \
-w /out/temp \
--skip_bids_validation \
--fd-spike-threshold 0.5 --dvars-spike-threshold 2.0 \
--bold2t1w-dof 9 --bold2t1w-init register \
--cifti-output \
--output-spaces fsLR MNI152NLin2009cAsym T1w fsaverage fsnative \
--ignore slicetiming sbref \
--fs-subjects-dir /work/data/derivatives/fmriprep/sourcedata/freesurfer