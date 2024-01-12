import json as js

data_dir = '/scratch/mgilson/braint/'

# subject indices to modify
subs = range(1,11)

for i_sub in subs:

    sub = 'sub-{}'.format(str(i_sub).zfill(3))

    # ses-01
    filepaths = ['{0}{1}/ses-01/fmap/{1}_ses-01_dir-AP_epi.json'.format(data_dir, sub),
                 '{0}{1}/ses-01/fmap/{1}_ses-01_dir-PA_epi.json'.format(data_dir, sub)]

    for filepath in filepaths:

        with open(filepath) as f:
            jf = js.load(f)

        print(jf)

        jf['IntendedFor'] = [
            'ses-01/func/{}_ses-01_task-rest_bold.nii.gz'.format(sub)
            ]

        print(jf)

        with open(filepath, 'w') as f:
            js.dump(jf, f, indent=8, separators=(',', ': '))


    # ses-02
    filepaths = ['{0}{1}/ses-02/fmap/{1}_ses-02_dir-AP_epi.json'.format(data_dir, sub),
                 '{0}{1}/ses-02/fmap/{1}_ses-02_dir-PA_epi.json'.format(data_dir, sub)]

    for filepath in filepaths:

        with open(filepath) as f:
            jf = js.load(f)

        print(jf)

        jf['IntendedFor'] = [
            'ses-02/func/{}_ses-02_task-01RestingCross_bold.nii.gz'.format(sub),
            'ses-02/func/{}_ses-02_task-02RetinoMultibar_bold.nii.gz'.format(sub),
            'ses-02/func/{}_ses-02_task-03ArchiLocalizer_bold.nii.gz'.format(sub),
            'ses-02/func/{}_ses-02_task-04ArchiSpatial_bold.nii.gz'.format(sub),
            'ses-02/func/{}_ses-02_task-05ArchiEmo_bold.nii.gz'.format(sub),
            'ses-02/func/{}_ses-02_task-06ArchiSocial_bold.nii.gz'.format(sub),
            'ses-02/func/{}_ses-02_task-07BodyLocalizer_bold.nii.gz'.format(sub),
            'ses-02/func/{}_ses-02_task-08VoiceLocalizer_bold.nii.gz'.format(sub),
            'ses-02/func/{}_ses-02_task-09RestingCross_bold.nii.gz'.format(sub)
            ]

        print(jf)

        with open(filepath, 'w') as f:
            js.dump(jf, f, indent=8, separators=(',', ': '))

