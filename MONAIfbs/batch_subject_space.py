#!/usr/bin/env python
#
# Instructions:
# Batch build subject_space_seg.nii.gz file. 
# seg_CurrentDate
#   |__PseudoAcc_PseudoName
#   |    |__SeriesNumber_AX_HeightxWidth
#   |    |    |__dcm
#   |    |    |__nifti
#   |    |    |__seg
#   |    |__SeriesNumber_COR_HeightxWidth
#   |    |__SeriesNumber_SAG_HeightxWidth
#   |    |__srr
#   |__PseudoAcc_PseudoName
#
# table series State
#     0: import from orthanc
#     1: SeriesDescription AX/COR/SAG
#     2: fatal_brain_seg OK
#     3: selected to reconstruction
#     4: reconstructoion OK
#     5: no template dir
#     6: no subject dir
#     9: target stack
#
# \author     Xuchu Liu (xuchu_liu@rush.edu)
# \date       04/05/2021
#

import sys
import os
import time
import fetaldb
import nibabel as nib
import numpy as np

if len(sys.argv) < 2:
    print("""
# Batch build subject_space_seg.nii.gz file. 

Usage: %s CurrentDate_sub
""" % (sys.argv[0]))
    exit(-1)

dbFile = "FetalMRIsqlite3.db"

input_path = sys.argv[1].rstrip('/')

#setup start time
t0 = time.time()

##########
conn = fetaldb.FetalDB(dbFile)

# SELECT State == 5
total_sub = 0
succ_sub = 0
pseudoid_dict = conn.select_series_pseudoid('5')
for (key, value) in pseudoid_dict.items():
    # for each AccNumber
    srr_path = input_path + '/' + value
    if not os.path.exists(srr_path):
        continue
    else:
        total_sub = total_sub + 1
        if os.path.exists(srr_path + "/recon_subject_space"):
            subject_path = srr_path + '/recon_subject_space/'
            subject_file = subject_path + 'srr_subject.nii.gz'
            mask_file = subject_path + 'srr_subject_mask.nii.gz'
            fetal_file = input_path + '/' + value + '_subject.nii.gz'
            if os.path.isfile(subject_file) and os.path.isfile(mask_file):
                subject_img = nib.load(subject_file)
                subject_img_data = subject_img.get_fdata()
                mask_img = nib.load(mask_file)
                mask_img_data = mask_img.get_fdata()
                fetal_img_affine = subject_img.affine.copy()
                fetal_img_header = subject_img.header.copy()
                fetal_img_data = subject_img_data * mask_img_data
                # fetal_img = nib.Nifti1Pair(fetal_img_data, np.eye(4))
                fetal_img = nib.Nifti1Image(fetal_img_data, fetal_img_affine, fetal_img_header)
                nib.save(fetal_img, fetal_file)
                succ_sub = succ_sub + 1
                print(fetal_file + " OK.")
            else:
                print('\033[1;35mCreate ', fetal_file, ' error. \033[0m')


conn.close()

#setup stop time
t1 = time.time()
total_time = t1-t0
hours = int(total_time/3600)
minutes = int((total_time - hours*3600)/60)
seconds = total_time - hours*3600 - minutes*60
print(f'Build subject space segment took {hours:d}:{minutes:02d}:{seconds:.3f}')
print('Total:' + str(total_sub) + ' Success:' + str(succ_sub) + \
    ' Error:' + str(total_sub - succ_sub)) 
