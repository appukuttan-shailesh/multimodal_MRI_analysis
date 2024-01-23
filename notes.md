

## File transfer and management at mesocentre

- copy fmriprep output files from mesocentre: `scp -rp -P 8822 <username>@login.mesocentre.univ-amu.fr:/scratch/braint/derivatives/fmriprep/<filename> <loca_dir>`

- copy files to mesocentre: `scp -rp -P 8822 <local_path_to_filename> <username>@login.mesocentre.univ-amu.fr:/scratch/braint/<remote_path>`

- make alias to mount/unmount remote directory (copy lines to .bashrc) using sshfs on ubuntu:
    - `alias mmeso='sshfs -p 8822 <username>@login.mesocentre.univ-amu.fr:/scratch/mgilson/braint/ -o auto_cache,reconnect <local_mount_dir>'`
    - `alias umeso='fusermount -u <local_mount_dir>'`

- change file permissions of generated files to allow access for all group members:
    - `chmod -Rf 771 /scratch/mgilson/braint` with '771' being read/write/execute for owner and group members, only execute for others
    - `chgrp -Rf 347 /scratch/mgilson/braint` with '347' the mesocentre project number

## Preparation for fmriprep

- create singularity image for fmriprep: `singularity build /scratch/mgilson/braint/code/singularity/fmriprep-23.2.0.simg docker://nipreps/fmriprep:23.2.0`
    - check the latest version on [https://fmriprep.org/en/stable/](https://fmriprep.org/en/stable/) to replace '23.2.0'

- fixing jason description files for fmap: `python3 fix_json_fmap.py` in '/scratch/mgilson/braint/code/preproc/'
    - to use python on mesocentre, use `module load python3` then `python3 <script.py>`

## Launching jobs on mesocentre using slurm

- go to '/scratch/mgilson/braint/code/job_launch/' and simply execute `sbatch sub-<idx>_fmriprep.sh` with the index *idx* of the subject
    - new launch scripts "for new subjects can be generated using 'gen_launch_scripts.py'
    - check progress using `squeue -u <username>` (your login for mesocentre)
    
## Create python environment

- with conda: https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html
- without conda: [https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments)
- create requirement.txt file: 
- activate environment in slurm script: `source <path-to-env>/activate`
