#!/usr/bin/env python
# coding: utf-8


#%% libraries

import os, sys
from pathlib import Path
from os.path import join

import chardet as cd

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt

from nilearn.plotting import plot_event


#%% subject and task information

print(sys.argv)

if True:
    # called from another process
    if not len(sys.argv)==3:
        raise ValueError('must provide subject and task indices')
    
    # subject tag
    sub = '{:03d}'.format(int(sys.argv[1]))
    
    # task tag
    tasks = ['task-03ArchiLocalizer', 'task-04ArchiSpatial', 'task-05ArchiEmo', 'task-06ArchiSocial', 'task-07BodyLocalizer', 'task-08VoiceLocalizer']
    task = tasks[int(sys.argv[2])]
else:
    sub = '002'
    task = 'task-03ArchiLocalizer'

print(sub, task)


#%% paths and filenames

# events (inputs)
event_sub_dir = '/home/INT/gilson.m/Neuro/projects/BraINT/BRAINT_behav/BRAINT/sourcedata/sub-{0:s}/ses-02/'.format(sub)
event_filename_tag = 'sub-{0:s}_ses-02_{1:s}'.format(sub, task)


# outputs
data_dir = '/home/INT/gilson.m/Neuro/projects/BraINT/derivatives_fmriprep/'
out_dir = data_dir + 'GLM_output/'

out_sub_dir = out_dir + 'sub-{0:s}/'.format(sub)
if not os.path.exists(out_sub_dir):
    os.mkdir(out_sub_dir)

output_filename = out_sub_dir + '{0:s}_events.tsv'.format(task)


#%% load event file

# find file name
for fname in os.listdir(event_sub_dir):
    if event_filename_tag in fname and 'txt' in fname \
       and (not 'Tapping' in fname) and (not '.~' in fname):
        print('found event file:', fname)
        event_filename = event_sub_dir + fname


# determine the encoding, which is not standard here
with open(event_filename, 'rb') as f:
    encoding = cd.detect(f.read())
print(encoding)

# load events as pandas data frame
df_orig = pd.read_csv(event_filename, encoding=encoding['encoding'], delimiter='\t')
print(df_orig)


#%% extract event onsets and durations

# DataFrame for events: condition, onset, duration; time in seconds for nilearn
df_ev = pd.DataFrame()

# previous condition to check blocks
prev_cond = ''
# initialize duration and onset (in seconds)
duration = -1.0
onset = -1.0
onset2 = -1.0

# iterate over rows348156
for l in df_orig[['CONDITIONS', 'ONSETS_MS', 'ONSETS_TRIGGERS', 'DURATIONS']].iterrows():
    # get values
    _, (cur_cond, cur_ons2, cur_ons, cur_dur) = l
    # check if equality between current and past values for condition
    if cur_cond==prev_cond:
        duration += cur_dur
    else:
        # add row to DataFrame (conversion of onset and duration from trigger to seconds, 1 trigger = 80 ms; conversion of onset 2 from ms to s)
        if not prev_cond=='':
            df_tmp = pd.DataFrame({'condition': prev_cond, 'onset2': onset2 / 1000.0, 'onset': onset * 0.08, 'duration': duration * 0.08}, [0])
            df_ev = pd.concat((df_ev, df_tmp), ignore_index=True)
        # move to next block
        prev_cond = cur_cond
        onset2 = cur_ons2
        onset = cur_ons
        duration = cur_dur
        
        
# optional sanity checks
if True:
    print('sanity check:\n')
    # if onsets are similar in ms and trigger
    print(df_ev)
    print()
    # display all conditions
    print(np.unique(df_ev['condition']))


#%% task-specific condition tags

if task=='task-03ArchiLocalizer':
    # list of conditions
    condition_ids = [
        'rest', # inter-trial interval
        'vertical checkerboard', 'horizontal checkerboard',
        'left button press, visual instructions',
        'left button press, auditory instructions',
        'right button press, visual instructions',
        'right button press, auditory instructions',
        'mental computation, visual instructions',
        'mental computation, auditory instructions',
        'visual sentence', 'auditory sentence'
    ]
    # trial conditions
    trial_cond = [condition_ids[i] for i in df_ev['condition']]

elif task=='task-04ArchiSpatial':
    condition_ids = [
        'BASELINE', 'IBI', # initial block and inter-block interval
        'object_grasp', 'object_orientation', 'rotation_hand', 'rotation_side',
        'saccade'
    ]
    # trial conditions
    trial_cond = df_ev['condition']

elif task=='task-05ArchiEmo':
    condition_ids = [
        'BASELINE', 'IBI', # initial block and inter-block interval
        'expression_control', 'expression_gender',
        'expression_intention', 
        'face_control', 'face_gender', 'face_trusty'
    ]
    # trial conditions
    trial_cond = df_ev['condition']

elif task=='task-06ArchiSocial':
    condition_ids = [
        'BASELINE', 'ITI', # initial block and inter-trial interval
        'false_belief_audio', 'false_belief_audio_pourquoi',
        'false_belief_video', 'false_belief_video_pourquoi',
        'mechanistic_audio', 'mechanistic_audio_pourquoi',
        'mechanistic_video', 'mechanistic_video_pourquoi',
        'non_speech', 'speech',
        'triangle_intention', 'triangle_random'
    ]
    # trial conditions
    trial_cond = df_ev['condition']

elif task=='task-07BodyLocalizer':
    condition_ids = [ # initial block and inter-trial interval
        'BASELINE', 'Blank',
        'HumanA', 'HumanH', 'HumanN', 'Nonhuman'
    ]
    # trial conditions
    trial_cond = df_ev['condition']

elif task=='task-08VoiceLocalizer':
    condition_ids = [
        'ITI', # inter-trial interval
        'animal', 'artificial', 'emotional', 'environmental', 'non_speech'
        'speech'
    ]
    # trial conditions
    trial_cond = df_ev['condition']



#%% save event file (type, onset, duration)

events = pd.DataFrame(
    {
        "trial_type": trial_cond,
        "onset": df_ev['onset'],
        "duration": df_ev['duration'],
    }
)

print(events)

# save as tsv file
events.to_csv(output_filename, sep="\t", index=False)
print('event data saved to {}'.format(output_filename))


# make figure
plot_event(events, figsize=(15, 5))
plt.savefig(out_sub_dir+'{}_events.png'.format(task))
plt.close()

