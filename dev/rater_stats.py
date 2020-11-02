import os
import random
import shutil
import nibabel
import numpy as np
import pandas as pd
from skimage import measure
from ivadomed import transforms as imed_transforms
from scipy.ndimage import zoom

def subjectFilter(input):
    if("sub" in input):
        return True
    else:
        return False


def compute_majority(dict):
    new_dict = {}
    for rater in dict:
        hspace = 0.25
        wspace = 0.25
        dspace = 2
        zooms = (dict[rater])[2]
        hfactor = zooms[0] / hspace
        wfactor = zooms[1] / wspace
        dfactor = zooms[2] / dspace
        params_resample = (hfactor, wfactor, dfactor)
        # Run resampling
        data_out = zoom((dict[rater])[1],
                        zoom=params_resample,
                        order=1)

        print(data_out.shape)
        crop = imed_transforms.CenterCrop([128, 128,15])
        metadata = {}
        metadata['crop_params'] = {}
        print(crop(data_out,metadata)[0].shape)
        new_dict[rater] = ((dict[rater])[0], crop(data_out,metadata)[0])
#contrasts = ["FLAIR", "ce-T1w", "PD", "T1w", "T2w"]
contrasts = ["T2star"]
#ms brain
#deriv_path = "/scratch/ms_brain/_BIDS_sameResolution/derivatives/labels"
#deriv_path = "/scratch/ms_brain/_BIDS/derivatives/labels"
#gm
deriv_path = "../duke/projects/ivadomed/gm_challenge_16_inter_rater/derivatives/labels"

subjects=list(filter(subjectFilter,os.listdir(deriv_path)))
print(subjects)

df = pd.DataFrame()
df2 = pd.DataFrame()
for subject in subjects:
    files = os.listdir(os.path.join(deriv_path,subject,"anat"))
    niis = [file for file in files if any(contrast in file for contrast in contrasts)]
    dict = {}
    print(subject)
    for nii in niis:
        base_name = "_".join((nii.split("_"))[0:2])
        rater = ((nii.split("_")[-1]).split(".")[0])[-1]
        if rater.isnumeric():

            #if rater == "n":

            #If we want to use majority instead of staples for MS brain
            #if rater != 0:
                fname = os.path.join(deriv_path,subject,"anat",nii)
                im1 = nibabel.load(fname).get_data()
                zooms = nibabel.load(fname).header.get_zooms()
                #print(zooms)
                im1[im1 > 0] = 1
                #im1[im1 < 0.5] = 0
                dict[rater] = (base_name,im1,zooms)
                labels = measure.label(im1)
                df = df.append({'file': base_name, 'rater': rater, 'lesion_count': labels.max(), 'positive_voxels': np.count_nonzero(im1)}, ignore_index=True)
                #print(base_name)
                #print(rater)
    #print(dict)
    #compute_majority(dict)

    #Majority voting for gm
    sum = np.zeros((dict["1"][1]).shape)
    for key in dict:
        sum += dict[key][1]
    threshold = 2
    im1 = np.where(sum >= threshold, 1, 0)
    dict["0"] = (None, im1, None)
    labels = measure.label(im1)
    df = df.append({'file': "", 'rater': "0", 'lesion_count': labels.max(), 'positive_voxels': np.count_nonzero(im1)}, ignore_index=True)

    gt = (dict["0"])[1]
    for key in dict:
        if key != "0":
            im1 = (dict[key])[1]
            #Threshold since some files have 3 values [0, 0.2, 1]
            TP = np.count_nonzero(np.logical_and(im1, gt))
            FP = np.count_nonzero(np.logical_and(im1, np.logical_not(gt)))
            FN = np.count_nonzero(np.logical_and(np.logical_not(im1), gt))
            TN = np.count_nonzero(np.logical_and(np.logical_not(im1), np.logical_not(gt)))
            total = np.size(gt)
            df2 = df2.append({'file': (dict[key])[0], 'rater': key, 'TP': TP/total, 'FP': FP/total, 'FN': FN/total, 'TN': TN/total}, ignore_index=True)

print(df.head(30))
df.to_csv('rater_lesion_stats.csv')
df2.to_csv('rater_voxel_stats.csv')