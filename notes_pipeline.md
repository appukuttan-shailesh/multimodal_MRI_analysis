

# File transfer with mesocentre

- copy files from mesocentre: scp -rp -P 8822 <username>@login.mesocentre.univ-amu.fr:/scratch/braint/derivatives/fmriprep/<filename> <loca_dir>

- make alias to mount/unmount remote directory (copy lines to .bashrc) using sshfs on ubuntu:
    - `alias mmeso='sshfs -p 8822 <username>@login.mesocentre.univ-amu.fr:/scratch/mgilson/braint/ -o auto_cache,reconnect <local_mount_dir>'`
    - `alias umeso='fusermount -u <local_mount_dir>'`

- change file permissions of generated files to allow access for all group members:
    - chmod -Rf 771 /scratch/mgilson/braint
    - chgrp -Rf 347 /scratch/mgilson/braint


