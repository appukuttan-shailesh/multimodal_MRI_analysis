'''Surface-test'''

from nilearn import image, plotting, surface
from nilearn.image import mean_img
from nilearn.surface import load_surf_data, load_surf_mesh
from nilearn.plotting import plot_design_matrix
import nibabel as nb
import numpy as np


from nilearn.plotting import plot_epi, show, plot_surf, plot_surf_stat_map
import matplotlib.pyplot as plt

t_r = 1.12
#slice_time_ref = 0.5

#%%

my_fmri_path = "C:\\Users\\andre\\Desktop\\sub-010\\sub-010_ses-02_task-03ArchiLocalizer_hemi-L_space-fsnative_bold.func.gii"

#load image
my_fmri = nb.load(my_fmri_path)
data_hemi = [x.data for x in my_fmri.darrays]
data_hemi = np.vstack(data_hemi)

#get numpy array from the image
#my_np_fmri = image.get_data(my_fmri)
#get mean fmri image
#my_mean_fmri = mean_img(my_fmri)


#%%

import pandas as pd

events_path = "C:\\Users\\andre\\Desktop\\sub-010\\events_labelled_no_rest.xlsx"

events = pd.read_excel(events_path)
events.drop(columns='Unnamed: 0', inplace=True)

#%%

import nilearn
#sub-010_hemi-L_inflated.surf.gii
#sub-010_hemi-L_pial.surf.gii
surface_path = "C:\\Users\\andre\\Desktop\\sub-010\\sub-010_hemi-L_inflated.surf.gii"
my_surface = load_surf_mesh(surface_path)


#plot_surf(my_surface)
#plt.show()

#%%

import numpy as np

n_scans = data_hemi.shape[0]
frame_times = t_r * (np.arange(n_scans) + .5)

#%%

confound = pd.read_excel("C:\\Users\\andre\\Desktop\\sub-010\\confoundss.xlsx")

confounds_of_interest = ['trans_x', 'trans_y', 'trans_z', 'rot_x', 'rot_y', 'rot_z',
                         'trans_x_derivative1', 'trans_x_power2',
                         'trans_y_derivative1', 'trans_y_power2',
                         'trans_z_derivative1', 'trans_z_power2']

confound_ok = confound[confounds_of_interest]
confound_ok.fillna(0, inplace=True)

#%%

from nilearn.glm.first_level import make_first_level_design_matrix

design_matrix = make_first_level_design_matrix(frame_times,
                                               events=events,
                                               hrf_model='spm',
                                               add_regs=confound_ok
                                               )

plot_design_matrix(design_matrix)
plt.show()

#%%

from nilearn.glm.first_level import run_glm

labels, estimates = run_glm(data_hemi, design_matrix.values, noise_model='ols')

#%%

contrast_matrix = np.eye(design_matrix.shape[1])

basic_contrasts = dict([(column, contrast_matrix[i])
                        for i, column in enumerate(design_matrix.columns)])

#%%

conditions = {"01_vertical_checkerboard": np.zeros(30),
              "02_horizontal_checkerboard": np.zeros(30),
              "03_visual_left_hand_button_press": np.zeros(30),
              "04_audio_left_hand_button_press": np.zeros(30),
              "05_visual_right_hand_button_press": np.zeros(30),
              "06_audio_right_hand_button_press": np.zeros(30),
              "07_visual_computation": np.zeros(30),
              "08_audio_computation": np.zeros(30),
              "09_sentence_reading": np.zeros(30),
              "10_sentence_listening": np.zeros(30)
              }

conditions["01_vertical_checkerboard"][0] = 1
conditions["02_horizontal_checkerboard"][1] = 1
conditions["03_visual_left_hand_button_press"][2] = 1
conditions["04_audio_left_hand_button_press"][3] = 1
conditions["05_visual_right_hand_button_press"][4] = 1
conditions["06_audio_right_hand_button_press"][5] = 1
conditions["07_visual_computation"][6] = 1
conditions["08_audio_computation"][7] = 1
conditions["09_sentence_reading"][8] = 1
conditions["10_sentence_listening"][9] = 1

audio = conditions["04_audio_left_hand_button_press"]+conditions["06_audio_right_hand_button_press"]+conditions["08_audio_computation"]+conditions["10_sentence_listening"]
visual = conditions["03_visual_left_hand_button_press"]+conditions["05_visual_right_hand_button_press"]+conditions["07_visual_computation"]+conditions["09_sentence_reading"]
computation = conditions["07_visual_computation"] + conditions["08_audio_computation"]
sentence = conditions["10_sentence_listening"] + conditions["09_sentence_reading"]
right = conditions["06_audio_right_hand_button_press"]+conditions["05_visual_right_hand_button_press"]
left = conditions["04_audio_left_hand_button_press"]+conditions["03_visual_left_hand_button_press"]

hor_ver = conditions["02_horizontal_checkerboard"] - conditions["01_vertical_checkerboard"]
aud_vis = audio - visual
right_left = right - left
comp_sent = computation - sentence

#%%

from nilearn import plotting
from nilearn.glm.contrasts import compute_contrast

contrast = compute_contrast(labels, estimates, comp_sent,
                            contrast_type='t')
z_score = contrast.z_score()

#infl_left = "C:\\Users\\andre\\Desktop\\sub-010\\sub-010_hemi-L_inflated.surf.gii"
#curv_right_sign = np.sign(curv_right)
plotting.plot_surf_stat_map(
        surface_path, z_score, hemi='left',
        title='c-s', colorbar=True,
        threshold=3.0)

plotting.show()

#%%

#mesh_path = "C:\\Users\\andre\\Desktop\\sub-010\\sub-010_hemi-L_pial.surf.gii"
#mesh_ = surface.load_surf_mesh(mesh_path)
#fmri_path = "C:\\Users\\andre\\Desktop\\sub-010\\sub-010_ses-02_task-03ArchiLocalizer_hemi-L_space-fsnative_bold.func.gii"
#fmri_ = surface.load_surf_data(fmri_path)
#plotting.plot_surf(mesh_, surf_map=fmri_[:, 10], hemi='left')

