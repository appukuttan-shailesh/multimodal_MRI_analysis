#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 22 08:29:26 2024

@author: gilson.m
"""


import subprocess

#sub_idx = range(2,12)
sub_idx = range(2,9) # local computer
task_idx = range(6)

list_contrasts = [
        ['AUD-VIS', 'L-R'],
        ['OBJ-ROT'],
        ['EXP-FAC','GEND-CTRL'],
        ['FB-MC'],
        ['H-NH'],
        ['S-NS']
    ]

for i_sub in sub_idx:
    for i_task in task_idx:
        for contrast in list_contrasts[i_task]:
            # extract events
            cmd = 'python extract_task_events.py {0:d} {1:d}'.format(i_sub, i_task)
            print(cmd)
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
            sout, serr = p.communicate()
            for l in sout.split(b'\n'):
                print(l.decode('utf8'))
    
            # run GLM on volume for contrast
            cmd = 'python nilearn_GLM_volume.py {0:d} {1:d} {2:s}'.format(i_sub, i_task, contrast)
            print(cmd)
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
            sout, serr = p.communicate()
            for l in sout.split(b'\n'):
                print(l.decode('utf8'))

            # run GLM on surfacefor contrast
            cmd = 'python nilearn_GLM_surface.py {0:d} {1:d} {2:s}'.format(i_sub, i_task, contrast)
            print(cmd)
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
            sout, serr = p.communicate()
            for l in sout.split(b'\n'):
                print(l.decode('utf8'))
