import numpy
import json as js

path = '/envau/work/brainets/data/BraINT/XNAT-BRAINT_NIFTI-2023-combined/'

for i in range(3, 11):

    subj = 'sub-' + str(i).zfill(3)

    filepath_1 = path + subj + '/ses-01/fmap/' + subj + '_ses-01_dir-AP_epi.json'
    filepath_2 = path + subj + '/ses-02/fmap/' + subj + '_ses-02_dir-AP_epi.json'

    print(filepath_1)

    with open(filepath_1) as f:
        jf = js.load(f)

    print(jf)

    jf["IntendedFor"] = [
            "ses-01/func/" + subj + "_ses-01_task-rest_bold.nii.gz",
            "ses-01/func/" + subj + "_ses-01_task-rest_sbref.nii.gz"    ]

    print(jf)

    with open(filepath_1, 'w') as f:
        js.dump(jf, f, indent=8, separators=(',', ': '))



    print(filepath_2)

    with open(filepath_2) as ff:
        jff = js.load(ff)

    print(jff)

    jff["IntendedFor"] = [
            "ses-02/func/" + subj + "_ses-02_task-01RestingCross_bold.nii.gz",
            "ses-02/func/" + subj + "_ses-02_task-01RestingCross_sbref.nii.gz",
            "ses-02/func/" + subj + "_ses-02_task-02RetinoMultibar_bold.nii.gz",
            "ses-02/func/" + subj + "_ses-02_task-02RetinoMultibar_sbref.nii.gz",
            "ses-02/func/" + subj + "_ses-02_task-03ArchiLocalizer_bold.nii.gz",
            "ses-02/func/" + subj + "_ses-02_task-03ArchiLocalizer_sbref.nii.gz",
            "ses-02/func/" + subj + "_ses-02_task-04ArchiSpatial_bold.nii.gz",
            "ses-02/func/" + subj + "_ses-02_task-04ArchiSpatial_sbref.nii.gz",
            "ses-02/func/" + subj + "_ses-02_task-05ArchiEmo_bold.nii.gz",
            "ses-02/func/" + subj + "_ses-02_task-05ArchiEmo_sbref.nii.gz",
            "ses-02/func/" + subj + "_ses-02_task-06ArchiSocial_bold.nii.gz",
            "ses-02/func/" + subj + "_ses-02_task-06ArchiSocial_sbref.nii.gz",
            "ses-02/func/" + subj + "_ses-02_task-07BodyLocalizer_bold.nii.gz",
            "ses-02/func/" + subj + "_ses-02_task-07BodyLocalizer_sbref.nii.gz",
            "ses-02/func/" + subj + "_ses-02_task-08VoiceLocalizer_bold.nii.gz",
            "ses-02/func/" + subj + "_ses-02_task-08VoiceLocalizer_sbref.nii.gz",
            "ses-02/func/" + subj + "_ses-02_task-09RestingCross_bold.nii.gz",
            "ses-02/func/" + subj + "_ses-02_task-09RestingCross_sbref.nii.gz"    ]

    print(jff)

    with open(filepath_2, 'w') as ff:
        js.dump(jf, ff, indent=8, separators=(',', ': '))

#%%

#import numpy
#import json as js
#
#path = 'C:\\Users\\andre\\Desktop\\sub-010\\'
#
#for i in range(10, 11):
#
#    subj = 'sub-' + str(i).zfill(3)
#
#    filepath_1 = path + subj + '\\ses-01\\fmap\\' + subj + '_ses-01_dir-AP_epi.json'
#    filepath_2 = path + subj + '\\ses-02\\fmap\\' + subj + '_ses-02_dir-AP_epi.json'
#
#    print(filepath_1)
#
#    with open(filepath_1) as f:
#        jf = js.load(f)
#
#    print(jf)
#
#    jf["IntendedFor"] = [
#        "ses-01/func/" + subj + "_ses-01_task-rest_bold.nii.gz",
#        "ses-01/func/" + subj + "_ses-01_task-rest_sbref.nii.gz"]
#
#    print(jf)
#
#    with open(filepath_1, 'w') as f:
#        js.dump(jf, f, indent=8, separators=(',', ': '))
#
#
#
#    print(filepath_2)
#
#    with open(filepath_2) as ff:
#        jff = js.load(ff)
#
#    print(jff)
#
#    jff["IntendedFor"] = [
#        "ses-02/func/" + subj + "_ses-02_task-01RestingCross_bold.nii.gz",
#        "ses-02/func/" + subj + "_ses-02_task-01RestingCross_sbref.nii.gz",
#        "ses-02/func/" + subj + "_ses-02_task-02RetinoMultibar_bold.nii.gz",
#        "ses-02/func/" + subj + "_ses-02_task-02RetinoMultibar_sbref.nii.gz",
#        "ses-02/func/" + subj + "_ses-02_task-03ArchiLocalizer_bold.nii.gz",
#        "ses-02/func/" + subj + "_ses-02_task-03ArchiLocalizer_sbref.nii.gz",
#        "ses-02/func/" + subj + "_ses-02_task-04ArchiSpatial_bold.nii.gz",
#        "ses-02/func/" + subj + "_ses-02_task-04ArchiSpatial_sbref.nii.gz",
#        "ses-02/func/" + subj + "_ses-02_task-05ArchiEmo_bold.nii.gz",
#        "ses-02/func/" + subj + "_ses-02_task-05ArchiEmo_sbref.nii.gz",
#        "ses-02/func/" + subj + "_ses-02_task-06ArchiSocial_bold.nii.gz",
#        "ses-02/func/" + subj + "_ses-02_task-06ArchiSocial_sbref.nii.gz",
#        "ses-02/func/" + subj + "_ses-02_task-07BodyLocalizer_bold.nii.gz",
#        "ses-02/func/" + subj + "_ses-02_task-07BodyLocalizer_sbref.nii.gz",
#        "ses-02/func/" + subj + "_ses-02_task-08VoiceLocalizer_bold.nii.gz",
#        "ses-02/func/" + subj + "_ses-02_task-08VoiceLocalizer_sbref.nii.gz",
#        "ses-02/func/" + subj + "_ses-02_task-09RestingCross_bold.nii.gz",
#        "ses-02/func/" + subj + "_ses-02_task-09RestingCross_sbref.nii.gz"    ]
#
#    print(jff)
#
#    with open(filepath_2, 'w') as ff:
#        js.dump(jff, ff, indent=8, separators=(',', ': '))




