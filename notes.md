

## File transfer and management at mesocentre

- identification to transfer files (also works with pharo/niolon to store on envau)
    - add ssh key for mesocentre (cf. [https://mesocentre.univ-amu.fr/copernicus](https://mesocentre.univ-amu.fr/copernicus)) to `~/.ssh/` in home directory in pharo/niolon
    - if needed, start ssh agent with `eval "$(ssh-agent)"` and add key with `ssh-add ~/.ssh/<key_file>`
    - further information: [link to mesocentre website](https://mesocentre.univ-amu.fr/connexion/)

- use `scp` or `rsync` to transfer files, for example
    - copy fmriprep output files from mesocentre: `scp -rp -P 8822 <username>@login.mesocentre.univ-amu.fr:/scratch/mgilson/braint/derivatives/fmriprep/<filename> <loca_dir>`
    - copy files to mesocentre: `scp -rp -P 8822 <local_path_to_filename> <username>@login.mesocentre.univ-amu.fr:/scratch/mgilson/braint/<remote_path>`

- make aliases to mount/unmount remote directory (copy lines to .bashrc) using sshfs on ubuntu
    - mount: `alias mmeso='sshfs -p 8822 <username>@login.mesocentre.univ-amu.fr:/scratch/mgilson/braint/ -o auto_cache,reconnect <local_mount_dir>'`
    - unmount: `alias umeso='fusermount -u <local_mount_dir>'`
    - if needed, install sshfs with apt or apt-get (sudo mode)

- change file permissions of generated files to allow access for all group members:
    - `chmod -Rf 771 /scratch/mgilson/braint`
    - `chgrp -Rf <gp_id> /scratch/mgilson/braint` where `<gp_id>` is the group number, 347 for BraINT

## Preparation for fmriprep

- create singularity image for fmriprep: `singularity build /scratch/mgilson/braint/code/singularity/fmriprep-23.2.0.simg docker://nipreps/fmriprep:23.2.0`
    - check the latest version on [https://fmriprep.org/en/stable/](https://fmriprep.org/en/stable/) to replace '23.2.0'

- fixing jason description files for fmap: `python3 fix_json_fmap.py` in folder '/scratch/mgilson/braint/code/preproc/'
    - link to script [fix_json_fmap.py](https://github.com/brainets/multimodal_MRI_analysis/blob/main/preproc/fix_json_fmap.py)
    - to use python on mesocentre, use `module load python3` then `python3 <script.py>`

## Launching jobs on mesocentre using slurm

- go to '/scratch/mgilson/braint/code/job_launch/' and simply execute `sbatch sub-<idx>_fmriprep.sh` with the index *idx* of the subject
    - new launch scripts 'sub-<idx>_fmriprep.sh' for new subjects can be generated using [gen_launch_scripts.py](https://github.com/brainets/multimodal_MRI_analysis/blob/main/preproc/gen_launch_scripts.py)
    - check progress using `squeue -u <username>` (your login for mesocentre)
    - further information: [link to mesocentre website](https://mesocentre.univ-amu.fr/slurm/)
