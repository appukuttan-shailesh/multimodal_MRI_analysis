import numpy as np
import pandas as pd
import chardet as cd

from nilearn import image, plotting
from nilearn.image import mean_img
from nilearn.plotting import plot_contrast_matrix, plot_glass_brain, view_img_on_surf
from nilearn.glm.first_level import FirstLevelModel
from nilearn.plotting import plot_design_matrix
from nilearn.glm import threshold_stats_img

from bids.layout import BIDSLayout

# %%
# path to file
#path = "C:\\Users\\andre\\Desktop\\sub-010\\sub-010_ses-02_task-03ArchiLocalizer_23_05_10_09_56.txt"
path = "C:\\Users\\andre\\Desktop\\sub-011\\sub-011_ses-02_task-03ArchiLocalizer_23_05_23_15_22.txt"

# to determine the encoding, which is not standard here

with open(path, 'rb') as f:
    result = cd.detect(f.read())  # or readline if the file is large

print(result)

# %%

df_orig = pd.read_csv(path, encoding='ISO-8859-1', delimiter='\t')

print(df_orig)

# %%
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
    if cur_cond == prev_cond:
        duration += cur_dur
    else:
        # add row to DataFrame (conversion of onset and duration from trigger to seconds, 1 trigger = 80 ms; conversion of onset 2 from ms to s)
        #        print(cur_cond, onset, duration)
        if not prev_cond == '':
            df_tmp = pd.DataFrame({'trial_type': prev_cond, 'onset2': onset2 / 1000.0, 'onset': onset * 0.08,
                                   'duration': duration * 0.08}, [0])
            df_ev = pd.concat((df_ev, df_tmp), ignore_index=True)
        # move to next block
        prev_cond = cur_cond
        onset2 = cur_ons2
        onset = cur_ons
        duration = cur_dur

# %%
# check if onsets are similar in ms and trigger
print(df_ev)

# %%
# check all conditions
print(np.unique(df_ev['trial_type']))

# %%
print(df_ev[['onset', 'duration', 'trial_type']])

# %%

df_fin = df_ev[['onset', 'duration', 'trial_type']]
df_fin.to_excel("C:\\Users\\andre\\Desktop\\sub-011\\events.xlsx")

# %%
#define mapping between the original conditions [0-10] with labelled conditions

sentences = {
    0: "rest",
    1: "01_vertical_checkerboard",
    2: "02_horizontal_checkerboard",
    3: "03_visual_left_hand_button_press",
    4: "04_audio_left_hand_button_press",
    5: "05_visual_right_hand_button_press",
    6: "06_audio_right_hand_button_press",
    7: "07_visual_computation",
    8: "08_audio_computation",
    9: "09_sentence_reading",
    10: "10_sentence_listening"
}

df_fin['trial_type'] = df_fin['trial_type'].map(sentences)
df_fin_1 = df_fin[df_fin['trial_type'] != 'rest']

# df_fin['trial_type'] = df_fin['trial_type'].replace(sentences)
print(df_fin_1)

df_fin.to_excel("C:\\Users\\andre\\Desktop\\sub-011\\events_labelled.xlsx")
df_fin_1.to_excel("C:\\Users\\andre\\Desktop\\sub-011\\events_labelled_no_rest.xlsx")

#%%

confound = pd.read_excel("C:\\Users\\andre\\Desktop\\sub-011\\confounds.xlsx")

confounds_of_interest = ['trans_x', 'trans_y', 'trans_z', 'rot_x', 'rot_y', 'rot_z',
                         'trans_x_derivative1', 'trans_x_power2',
                         'trans_y_derivative1', 'trans_y_power2',
                         'trans_z_derivative1', 'trans_z_power2']

confound_ok = confound[confounds_of_interest]
confound_ok.fillna(0, inplace=True)

#%%
#Loading the fMRI image of interest

#"C:\\Users\\andre\\Desktop\\sub-010\\sub-010_ses-02_task-03ArchiLocalizer_space-T1w_desc-preproc_bold.nii.gz"
#sub-010_ses-02_task-03ArchiLocalizer_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz
#sub-010_ses-02_task-03ArchiLocalizer_space-T1w_desc-preproc_bold.nii.gz

#"C:\\Users\\andre\\Desktop\\sub-011\\sub-011\\ses-02\\func\\sub-011_ses-02_task-03ArchiLocalizer_space-T1w_desc-preproc_bold.nii.gz"
#"C:\\Users\\andre\\Desktop\\sub-011\\sub-011\\ses-02\\func\\sub-011_ses-02_task-03ArchiLocalizer_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz"

#my_fmri_path = "C:\\Users\\andre\\Desktop\\sub-010\\sub-010_ses-02_task-03ArchiLocalizer_space-T1w_desc-preproc_bold.nii.gz"
my_fmri_path = "C:\\Users\\andre\\Desktop\\sub-011\\sub-011\\ses-02\\func\\sub-011_ses-02_task-03ArchiLocalizer_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz"


#load image
my_fmri = image.load_img(my_fmri_path)
#get numpy array from the image
my_np_fmri = image.get_data(my_fmri)
#get mean fmri image
my_mean_fmri = mean_img(my_fmri)

# %%
# Define the paradigm that will be used
#
# This task comprises 10 conditions:
#
# * audio_left_hand_button_press: Left-hand three-times button press,
#   indicated by auditory instruction
# * audio_right_hand_button_press: Right-hand three-times button press,
#   indicated by auditory instruction
# * visual_left_hand_button_press: Left-hand three-times button press,
#   indicated by visual instruction
# * visual_right_hand_button_press:  Right-hand three-times button press,
#   indicated by visual instruction
# * horizontal_checkerboard: Visualization of flashing horizontal checkerboards
# * vertical_checkerboard: Visualization of flashing vertical checkerboards
# * sentence_listening: Listen to narrative sentences
# * sentence_reading: Read narrative sentences
# * audio_computation: Mental subtraction, indicated by auditory instruction
# * visual_computation: Mental subtraction, indicated by visual instruction
#

events_path = "C:\\Users\\andre\\Desktop\\sub-011\\events_labelled_no_rest.xlsx"

t_r = 1.12
events = pd.read_excel(events_path)
events.drop(columns='Unnamed: 0', inplace=True)

# %%
# Running a basic model
# ---------------------
#
# First we specify a linear model.
# The .fit() functionality of FirstLevelModel function creates the design
# matrix and the beta maps.
#

#first_level_model = FirstLevelModel(t_r)
first_level_model = FirstLevelModel(
    t_r=t_r,
    noise_model="ar1",
    standardize=False,
    hrf_model="spm",
    drift_model="cosine",
    high_pass=0.01,
    slice_time_ref=0.0,
    smoothing_fwhm=4
)

first_level_model = first_level_model.fit(my_fmri_path, events=events, confounds=confound_ok)
design_matrix = first_level_model.design_matrices_[0]

# %%
# Let us take a look at the design matrix: it has 10 main columns corresponding
# to 10 experimental conditions, followed by 3 columns describing low-frequency
# signals (drifts) and a constant regressor.

plot_design_matrix(design_matrix)
import matplotlib.pyplot as plt

plt.show()

# %%
# Specification of the contrasts.
#
# For this, let's create a function that, given the design matrix, generates
# the corresponding contrasts.  This will be useful to repeat contrast
# specification when we change the design matrix.

#def make_localizer_contrasts(design_matrix):
#    """Return a dictionary of four contrasts, given the design matrix."""
#    # first generate canonical contrasts
#    contrast_matrix = np.eye(design_matrix.shape[1])
#    contrasts = {
#        column: contrast_matrix[i]
#        for i, column in enumerate(design_matrix.columns)
#    }
#
#    print(contrasts)
#
#
#    contrasts["audio"] = (
#        contrasts["04_audio_left_hand_button_press"]
#        + contrasts["06_audio_right_hand_button_press"]
#        + contrasts["08_audio_computation"]
#        + contrasts["10_sentence_listening"]
#    )
#
#    print(contrasts)
#
#    # one contrast adding all conditions involving instructions reading
#    contrasts["visual"] = (
#        contrasts["03_visual_left_hand_button_press"]
#        + contrasts["05_visual_right_hand_button_press"]
#        + contrasts["07_visual_computation"]
#        + contrasts["09_sentence_reading"]
#    )
#
#    # one contrast adding all conditions involving computation
#    contrasts["computation"] = (
#        contrasts["07_visual_computation"] + contrasts["08_audio_computation"]
#    )
#
#    # one contrast adding all conditions involving sentences
#    contrasts["sentences"] = (
#        contrasts["10_sentence_listening"] + contrasts["09_sentence_reading"]
#    )
#
#    # Short dictionary of more relevant contrasts
#    contrasts = {
#        "left - right button press": (
#            contrasts["04_audio_left_hand_button_press"]
#            - contrasts["06_audio_right_hand_button_press"]
#            + contrasts["03_visual_left_hand_button_press"]
#            - contrasts["05_visual_right_hand_button_press"]
#        ),
#        "audio - visual": contrasts["audio"] - contrasts["visual"],
#        "computation - sentences": (
#            contrasts["computation"] - contrasts["sentences"]
#        ),
#        "horizontal-vertical": (
#            contrasts["02_horizontal_checkerboard"]
#            - contrasts["01_vertical_checkerboard"]
#        ),
#    }
#    return contrasts
#
#
## %%
## Let's look at these computed contrasts:
#
#contrasts = make_localizer_contrasts(design_matrix)
#
#for key, values in contrasts.items():
#    plot_contrast_matrix(values, design_matrix=design_matrix)
#    plt.suptitle(key)
#
#    plt.show()
#
## %%
## A first contrast estimation and plotting
## ----------------------------------------
##
## As this script will be repeated several times, we encapsulate model
## fitting and plotting in a function that we call when needed.
##
#
#def plot_contrast(first_level_model):
#    """Specify, estimate and plot the main contrasts \
#        for given a first model."""
#    design_matrix = first_level_model.design_matrices_[0]
#    # Call the contrast specification within the function
#    contrasts = make_localizer_contrasts(design_matrix)
#    plt.figure(figsize=(11, 3))
#    # compute the per-contrast z-map
#    for index, (contrast_id, contrast_val) in enumerate(contrasts.items()):
#        ax = plt.subplot(1, len(contrasts), 1 + index)
#        z_map = first_level_model.compute_contrast(
#            contrast_val, output_type="z_score"
#        )
#        plotting.plot_stat_map(
#            z_map,
#            bg_img=my_mean_fmri,
#            display_mode="z",
#            threshold=3.0,
#            title=contrast_id,
#            axes=ax,
#            cut_coords=1,
#        )
#
#
## %%
## Let's run the model and look at the outcome.
#
#plot_contrast(first_level_model)
#plt.show()
#
#design_matrix = first_level_model.design_matrices_[0]
#
#contrasts = make_localizer_contrasts(design_matrix)
#
#contrast_id = next(iter(contrasts))
##contrast_id = "audio - visual"
#
#contrast_val = contrasts[contrast_id]
#
##(contrast_id, contrast_val) = next(iter(contrasts))
#
#z_map = first_level_model.compute_contrast(contrast_id, output_type="z_score")
#
#plotting.plot_stat_map(
#    z_map,
#    bg_img=my_mean_fmri,
#    threshold=3.0,
#    display_mode="z",
#    cut_coords=10,
#    black_bg=True,
#    title=contrast_id,
#)
#plt.show()
#
#
#%% single plot

plt.plot(design_matrix["01_vertical_checkerboard"])
plt.xlabel("second")
plt.title("Expected vertical_checkerboard Response")
plt.show()

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

plot_contrast_matrix(comp_sent, design_matrix=design_matrix)
plt.show()

#%%

z_map = first_level_model.compute_contrast(aud_vis, output_type='stat') #z_score
_, threshold = threshold_stats_img(z_map, alpha=0.001, height_control="fpr")

plotting.plot_stat_map(
    z_map,
    bg_img=my_mean_fmri,
    threshold=threshold,
    display_mode="ortho",
    #cut_coords=10,
    black_bg=True,
    title="a-v"
)
plt.show()

#%%

z_map = first_level_model.compute_contrast(comp_sent, output_type='stat') #z_score
_, threshold = threshold_stats_img(z_map, alpha=0.001, height_control="fpr")

plotting.plot_stat_map(
    z_map,
    bg_img=my_mean_fmri,
    threshold=threshold,
    display_mode="z",
    cut_coords=10,
    black_bg=True,
    title="c-s"
)
plt.show()

#%%

z_map = first_level_model.compute_contrast(comp_sent, output_type='stat') #z_score

plotting.plot_glass_brain(z_map,
                 black_bg=True,
                 threshold=3.0,
                 plot_abs=False,
                 title='c-s')
plt.show()

#%%

from nilearn import datasets

fsaverage = datasets.fetch_surf_fsaverage()
aa = fsaverage.pial_right

z_map = first_level_model.compute_contrast(comp_sent, output_type='z_score') #z_score

plotting.plot_surf_stat_map(aa, z_map,
                 black_bg=True,
                 threshold=3.0,
                 title='c-s')
plt.show()


