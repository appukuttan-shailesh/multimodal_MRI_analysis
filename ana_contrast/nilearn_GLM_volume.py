#!/usr/bin/env python
# coding: utf-8


#%% libraries

import os, sys
from pathlib import Path

from os.path import join

import json
import chardet as cd

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt

import nibabel as nib

from nilearn.plotting import plot_event, plot_anat, plot_img, plot_design_matrix, plot_contrast_matrix
from nilearn.plotting import plot_stat_map, plot_surf_stat_map
from nilearn.glm.first_level import FirstLevelModel,make_first_level_design_matrix
from nilearn.glm import threshold_stats_img
from nilearn.reporting import get_clusters_table



#%% subject and task information

if True:
    # called from another process
    if not len(sys.argv)==4:
        raise ValueError('must provide subject and task indices')
    
    # subject tag
    sub = '{:03d}'.format(int(sys.argv[1]))
    
    # task tag
    tasks = ['task-03ArchiLocalizer', 'task-04ArchiSpatial', 'task-05ArchiEmo', 'task-06ArchiSocial', 'task-07BodyLocalizer', 'task-08VoiceLocalizer']
    task = tasks[int(sys.argv[2])]
    
    # contrast tag
    contrast = str(sys.argv[3])
    
    # space tag
    space = 'T1w' # space-T1w=vol, hemi-R_space-fsaverage
    
else:
    # for testing individual sessions
    sub = '007'
    task = 'task-05ArchiEmo'
    contrast = 'EXP-FAC'

print('sub, task, contrast: {:s}, {:s}, {:s}'.format(sub, task, contrast))


#%% paths and filenames

# directories
data_dir = '/home/INT/gilson.m/Neuro/projects/BraINT/derivatives_fmriprep/'
out_dir = data_dir + 'GLM_output/'
out_sub_dir = out_dir + 'sub-{0:s}/'.format(sub)
if not os.path.exists(out_sub_dir):
    raise ValueError('no folder for subject, was expecting to find {}'.format(out_sub_dir))

# formatted events (inputs)
event_filename = out_sub_dir + '{0:s}_events.tsv'.format(task)

# fMRI data (inputs)
data_sub_dir = data_dir + 'sub-{0:s}/ses-02/func/'.format(sub)

json_filename = data_sub_dir + 'sub-{0:s}_ses-02_{1:s}_space-T1w_desc-preproc_bold.json'.format(sub, task)
data_filename = data_sub_dir + 'sub-{0:s}_ses-02_{1:s}_space-T1w_desc-preproc_bold.nii.gz'.format(sub, task)
ref_filename = data_sub_dir + 'sub-{0:s}_ses-02_{1:s}_space-T1w_boldref.nii.gz'.format(sub, task)
cofound_filename = data_sub_dir + 'sub-{0:s}_ses-02_{1:s}_desc-confounds_timeseries.tsv'.format(sub, task)
mask_filename = data_sub_dir + 'sub-{0:s}_ses-02_{1:s}_space-T1w_desc-brain_mask.nii.gz'.format(sub, task)

# SURFACE DATA
# sub-002_ses-02_task-03ArchiLocalizer_hemi-R_space-fsaverage_bold.func.gii
# sub-002_ses-02_task-03ArchiLocalizer_space-fsLR_den-91k_bold.dtseries.nii
# sub-002_ses-02_task-03ArchiLocalizer_space-fsLR_den-91k_bold.dtseries.nii
# gifti_func=init_dir+"/derivatives/fmriprep/sub-011/ses-02/func/sub-011_ses-02_task-03ArchiLocalizer_hemi-R_space-fsnative_bold.func.gii"
# gifti_func_s=init_dir+"/derivatives/fmriprep/sub-011/ses-02/func/my_gii_smoothed2.func.gii"


#%% load formatted event file

events = pd.read_csv(event_filename, sep='\t')


#%% reference image

plt.figure()
plot_img(ref_filename, colorbar=True, cbar_tick_format="%i")
plt.savefig(out_sub_dir+'{}_fmri_ref.png'.format(task))


#%% build the confounds dataframe

confounds = pd.read_csv(cofound_filename,sep= '\t')

motion6 = confounds[["rot_x","rot_y","rot_z","trans_x",'trans_y','trans_z']]
motion24 = confounds[["rot_x","rot_y","rot_z","trans_x","trans_y","trans_z","rot_x_derivative1","rot_y_derivative1","rot_z_derivative1",
                       "trans_x_derivative1","trans_y_derivative1","trans_z_derivative1","rot_x_power2","rot_y_power2","rot_z_power2",
                       "trans_x_power2",'trans_y_power2','trans_z_power2',"rot_x_derivative1_power2","rot_y_derivative1_power2","rot_z_derivative1_power2",
                       "trans_x_derivative1_power2","trans_y_derivative1_power2","trans_z_derivative1_power2"]]

# regressor names
acompcor = [] 
for i in range(0,12):
    #acompcor=acompcor.append(['w_comp_cor_' + i])
    acompcor.append("w_comp_cor_"+f"{i:02d}")

acompcor_reg = confounds[acompcor]

pd.options.mode.chained_assignment = None
motion24[np.isnan(motion24)] = 0
#display(motion24)
#display(acompcor_reg)

nuisance = pd.concat([motion24,acompcor_reg],axis=1)
#print(nuisance)


#%% build a general linear model (GLM) for single session fMRI data

# task fMRI data
with open(json_filename, 'r') as f:
    t_r = json.load(f)['RepetitionTime']

fmri_glm = FirstLevelModel(
    t_r=t_r,
    noise_model="ar1",
    smoothing_fwhm=4,
    standardize=False,
    mask_img=mask_filename,
    hrf_model="spm",
    drift_model="cosine",
    high_pass=0.01,
)

data_img = nib.load(data_filename)
n_scans = data_img.shape[3] # the acquisition comprises 128 scans
frame_times = np.arange(n_scans) * t_r  # here are the corresponding frame times

# train GLM
fmri_glm = fmri_glm.fit(data_filename, events, nuisance)

# check desing matrix
design_matrix = fmri_glm.design_matrices_[0]

plt.figure()
plot_design_matrix(design_matrix)
plt.savefig(out_sub_dir+'{}_design_matrix.png'.format(task))


#%% contrast of interest
# !!! watchout for nilearn reordering of conditions columns based on alphabetical order !!!
# TODO, get conditions_idx from extract_task_events and sort them in alphabetical order to automatize code below

if task=='task-03ArchiLocalizer':
    conditions = {"rest": np.zeros(design_matrix.shape[1]),
                  "vertical checkerboard": np.zeros(design_matrix.shape[1]),
                  "horizontal checkerboard": np.zeros(design_matrix.shape[1]),
                  "left button press, auditory instructions": np.zeros(design_matrix.shape[1]),
                  "left button press, visual instructions": np.zeros(design_matrix.shape[1]),
                  "right button press, visual instructions": np.zeros(design_matrix.shape[1]),
                  "right button press, auditory instructions": np.zeros(design_matrix.shape[1]),
                  "mental computation, auditory instructions": np.zeros(design_matrix.shape[1]),
                  "mental computation, visual instructions": np.zeros(design_matrix.shape[1]),
                  "visual sentence": np.zeros(design_matrix.shape[1]),
                  "auditory sentence": np.zeros(design_matrix.shape[1]),
                 }
    
    # alphabetical order
    conditions["auditory sentence"][0] = 1
    conditions["horizontal checkerboard"][1] = 1
    conditions["left button press, auditory instructions"][2] = 1
    conditions["left button press, visual instructions"][3] = 1
    conditions["mental computation, auditory instructions"][4] = 1
    conditions["mental computation, visual instructions"][5] = 1
    conditions["rest"][6] = 1
    conditions["right button press, auditory instructions"][7] = 1
    conditions["right button press, visual instructions"][8] = 1
    conditions["vertical checkerboard"][9] = 1
    conditions["visual sentence"][10] = 1

    if contrast=='AUD-VIS':
        # contrast between conditions
        contrast_cond = conditions["left button press, auditory instructions"] \
                      + conditions["right button press, auditory instructions"] \
                      + conditions["mental computation, auditory instructions"] \
                      - conditions["left button press, visual instructions"] \
                      - conditions["right button press, visual instructions"] \
                      - conditions["mental computation, visual instructions"]
    elif contrast=='L-R':
        # contrast between conditions
        contrast_cond = conditions["left button press, auditory instructions"] \
                      + conditions["left button press, visual instructions"] \
                      - conditions["right button press, auditory instructions"] \
                      - conditions["right button press, visual instructions"] 
    else:
        raise ValueError('wrong contrast tag')
        
elif task=='task-04ArchiSpatial':
    conditions = {"BASELINE": np.zeros(design_matrix.shape[1]),
                  "IBI": np.zeros(design_matrix.shape[1]),
                  "object_grasp": np.zeros(design_matrix.shape[1]),
                  "object_orientation": np.zeros(design_matrix.shape[1]),
                  "rotation_hand": np.zeros(design_matrix.shape[1]),
                  "rotation_side": np.zeros(design_matrix.shape[1]),
                  "saccade": np.zeros(design_matrix.shape[1])
                 }

    # alphabetical order
    conditions["BASELINE"][0] = 1
    conditions["IBI"][1] = 1
    conditions["object_grasp"][2] = 1
    conditions["object_orientation"][3] = 1
    conditions["rotation_hand"][4] = 1
    conditions["rotation_side"][5] = 1
    conditions["saccade"][6] = 1

    if contrast=='OBJ-ROT':
        # contrast between conditions
        contrast_cond = conditions["object_grasp"] \
                      + conditions["object_orientation"] \
                      - conditions["rotation_hand"] \
                      - conditions["rotation_hand"]
    else:
        raise ValueError('wrong contrast tag')

elif task=='task-05ArchiEmo':
    conditions = {"BASELINE": np.zeros(design_matrix.shape[1]),
                  "IBI": np.zeros(design_matrix.shape[1]),
                  "expression_control": np.zeros(design_matrix.shape[1]),
                  "expression_gender": np.zeros(design_matrix.shape[1]),
                  "expression_intention": np.zeros(design_matrix.shape[1]),
                  "face_control": np.zeros(design_matrix.shape[1]),
                  "face_gender": np.zeros(design_matrix.shape[1]),
                  "face_trusty": np.zeros(design_matrix.shape[1])
                 }

    # alphabetical order
    conditions["BASELINE"][0] = 1
    conditions["expression_control"][1] = 1
    conditions["expression_gender"][2] = 1
    conditions["expression_intention"][3] = 1
    conditions["face_control"][4] = 1
    conditions["face_gender"][5] = 1
    conditions["face_trusty"][6] = 1
    conditions["IBI"][7] = 1

    if contrast=='EXP-FAC':
        # contrast between conditions
        contrast_cond = conditions["expression_control"] \
                      + conditions["expression_gender"] \
                      + conditions["expression_intention"] \
                      - conditions["face_control"] \
                      - conditions["face_gender"] \
                      - conditions["face_trusty"]
    elif contrast=='GEND-CTRL':
        # contrast between conditions
        contrast_cond = conditions["expression_gender"] \
                      + conditions["face_gender"] \
                      - conditions["expression_control"] \
                      - conditions["face_control"]
    else:
        raise ValueError('wrong contrast tag')

elif task=='task-06ArchiSocial':
    conditions = {"BASELINE": np.zeros(design_matrix.shape[1]),
                  "ITI": np.zeros(design_matrix.shape[1]),
                  "false_belief_audio": np.zeros(design_matrix.shape[1]),
                  "false_belief_audio_pourquoi": np.zeros(design_matrix.shape[1]),
                  "false_belief_video": np.zeros(design_matrix.shape[1]),
                  "false_belief_video_pourquoi": np.zeros(design_matrix.shape[1]),
                  "mechanistic_audio": np.zeros(design_matrix.shape[1]),
                  "mechanistic_audio_pourquoi": np.zeros(design_matrix.shape[1]),
                  "mechanistic_video": np.zeros(design_matrix.shape[1]),
                  "mechanistic_video_pourquoi": np.zeros(design_matrix.shape[1]),
                  "non_speech": np.zeros(design_matrix.shape[1]),
                  "speech": np.zeros(design_matrix.shape[1]),
                  "triangle_intention": np.zeros(design_matrix.shape[1]),
                  "triangle_random": np.zeros(design_matrix.shape[1])
                 }

    # alphabetical order
    conditions["BASELINE"][0] = 1
    conditions["false_belief_audio"][1] = 1
    conditions["false_belief_audio_pourquoi"][2] = 1
    conditions["false_belief_video"][3] = 1
    conditions["false_belief_video_pourquoi"][4] = 1
    conditions["ITI"][5] = 1
    conditions["mechanistic_audio"][6] = 1
    conditions["mechanistic_audio_pourquoi"][7] = 1
    conditions["mechanistic_video"][8] = 1
    conditions["mechanistic_video_pourquoi"][9] = 1
    conditions["non_speech"][10] = 1
    conditions["speech"][11] = 1
    conditions["triangle_intention"][12] = 1
    conditions["triangle_random"][13] = 1

    if contrast=='FB-MC':
        # contrast between conditions
        contrast_cond = conditions["false_belief_audio"] \
                      + conditions["false_belief_audio_pourquoi"] \
                      + conditions["false_belief_video"] \
                      + conditions["false_belief_video_pourquoi"] \
                      - conditions["mechanistic_audio"] \
                      - conditions["mechanistic_audio_pourquoi"] \
                      - conditions["mechanistic_video"] \
                      - conditions["mechanistic_video_pourquoi"]
    else:
        raise ValueError('wrong contrast tag')

elif task=='task-07BodyLocalizer':
    conditions = {"BASELINE": np.zeros(design_matrix.shape[1]),
                  "Blank": np.zeros(design_matrix.shape[1]),
                  "HumanA": np.zeros(design_matrix.shape[1]),
                  "HumanH": np.zeros(design_matrix.shape[1]),
                  "HumanN": np.zeros(design_matrix.shape[1]),
                  "Nonhuman": np.zeros(design_matrix.shape[1])
                 }

    # alphabetical order
    conditions["BASELINE"][0] = 1
    conditions["Blank"][1] = 1
    conditions["HumanA"][2] = 1
    conditions["HumanH"][3] = 1
    conditions["HumanN"][4] = 1
    conditions["Nonhuman"][5] = 1

    if contrast=='H-NH':
        # contrast between conditions
        contrast_cond = conditions["HumanA"] \
                      + conditions["HumanH"] \
                      + conditions["HumanN"] \
                      - conditions["Nonhuman"]
    else:
        raise ValueError('wrong contrast tag')

elif task=='task-08VoiceLocalizer':
    conditions = {"ITI": np.zeros(design_matrix.shape[1]),
                  "animal": np.zeros(design_matrix.shape[1]),
                  "artificial": np.zeros(design_matrix.shape[1]),
                  "emotional": np.zeros(design_matrix.shape[1]),
                  "environmental": np.zeros(design_matrix.shape[1]),
                  "non_speech": np.zeros(design_matrix.shape[1]),
                  "speech": np.zeros(design_matrix.shape[1])
                 }

    # alphabetical order
    conditions["animal"][0] = 1
    conditions["artificial"][1] = 1
    conditions["emotional"][2] = 1
    conditions["environmental"][3] = 1
    conditions["ITI"][4] = 1
    conditions["non_speech"][5] = 1
    conditions["speech"][6] = 1

    if contrast=='S-NS':
        # contrast between conditions
        contrast_cond = conditions["speech"] \
                      + conditions["emotional"] \
                      - conditions["non_speech"] \
                      - conditions["artificial"] \
                      - conditions["environmental"]
    else:
        raise ValueError('wrong contrast tag')


plt.figure()
plot_contrast_matrix(contrast_cond, design_matrix=design_matrix)
plt.savefig(out_sub_dir+'{}_contrast_design_matrix.png'.format(task))


#%% plot expected response for regressors



# plt.figure()
# plt.plot(design_matrix["auditory sentence"])
# plt.xlabel('frame index')
# plt.title('Expected auditory sentence Response')
# plt.savefig(out_sub_dir+'{}_exp_resp.png'.format(task))



#%% compute effect size (in )z-score)

# z-score map
z_map = fmri_glm.compute_contrast(contrast_cond, output_type='z_score')

# threshold using FDR
_, threshold = threshold_stats_img(z_map, alpha=0.05, height_control='fdr', cluster_threshold=10)
print('false Discovery rate = 0.05 with threshold={:.3f}, cluster>=10 voxels'.format(threshold))

plt.figure()
plot_stat_map(
    z_map,
    bg_img=ref_filename,
    threshold=threshold,
    display_mode="z",
    cut_coords=6,
    black_bg=True,
    title='{} (fdr=0.05, cluster>=10)'.format(contrast),
)
plt.savefig(out_sub_dir+'{}_contrast_{}.png'.format(task, contrast))



# table = get_clusters_table(
#     z_map, stat_threshold=threshold, cluster_threshold=20
# )
# table



# SURF DATA

# gifti_func = init_dir+"/derivatives_fmriprep/sub-002/ses-02/func/sub-002_ses-02_task-03ArchiLocalizer_hemi-R_space-fsaverage_bold.func.gii"
# gifti = nib.load(gifti_func)

# img_data = [x.data for x in gifti.darrays]
# data_hemiR = np.vstack(img_data)
# data_hemiR.shape

# json_file=init_dir+"/derivatives_fmriprep/sub-002/ses-02/func/sub-002_ses-02_task-03ArchiLocalizer_hemi-R_space-fsaverage_bold.json"

# with open(json_file, 'r') as f:
#     t_r = json.load(f)['RepetitionTime']

# n_scans = data_hemiR.shape[0]
# frame_times = t_r * (np.arange(n_scans) + .5)

# t_r = 1.12
# n_scans = cifti.shape[0]
# frame_times = t_r * (np.arange(n_scans) + .5)

# design_matrix = make_first_level_design_matrix(frame_times,
#                                                events=events,
#                                                hrf_model='spm',
#                                                add_regs=nuisance
#                                                )

# #labels, estimates = run_glm(texture.T, design_matrix.values)
# labels, estimates = run_glm(data_hemiRnew, design_matrix.values)

# contrast = compute_contrast(labels, estimates, contrast1,
#                                 contrast_type='t')
# contrast_id="Audio_minus_Visual"
# # we present the Z-transform of the t map
# z_score = contrast.z_score()

# curv_mesh = datasets.fetch_surf_fsaverage(mesh='fsaverage', data_dir=None)['infl_right']
# sulc_surf = datasets.fetch_surf_fsaverage(mesh='fsaverage', data_dir=None)['sulc_right']

# plotting.plot_surf_stat_map(
#     curv_mesh, z_score, hemi='right',
#     title=contrast_id, colorbar=True,
#     threshold=3., bg_map=sulc_surf, output_file=outdir/'contrast2.png')



