

# File transfer with mesocentre

- copy files: scp -rp -P 8822 <username>@login.mesocentre.univ-amu.fr:/scratch/braint/derivatives/fmriprep/<filename> <loca_dir>

- make alias to mount/unmount remote directory (copy lines to .bashrc):
`alias mmeso='sshfs -p 8822 mgilson@login.mesocentre.univ-amu.fr:/scratch/mgilson/ -o auto_cache,reconnect ~/Neuro/mesocentre/sshfs_scratch/'`
`alias umeso='fusermount -u ~/Neuro/mesocentre/sshfs_scratch/'`



