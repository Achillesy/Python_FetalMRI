#!/usr/bin/env python
#
# Instructions:
# Batch process fetal_brain_png.py to write seg to png. 
# seg
#   |__PseudoName_SeriesNumber_InstanceNumber_img
#   |    |__PseudoName_SeriesNumber_InstanceNumber_img_seg.nii.gz
# png
#
# \author     Xuchu Liu (xuchu_liu@rush.edu)
# \date       06/28/2021
#

import os
import numpy as np
import time
import nibabel as nib
from PIL import Image

#setup start time
t0 = time.time()

##########
total_fbs = 0
succ_dcm = 0

segFullnameList = []
cwd = os.getcwd()
curDir = os.walk(cwd)
for path, dir_list, file_list in curDir:
    for file_name in file_list:
        if 'seg.nii.gz' in file_name:
            total_fbs = total_fbs + 1
            segFullnameList.append([file_name, os.path.join(path, file_name)])

for seg_file, seg_fullname in segFullnameList:
    seg_img = nib.load(seg_fullname)
    seg_img_data = seg_img.get_fdata()
    img_data = np.squeeze(seg_img_data)
    img_data = img_data.astype(np.uint8)
    png_name = seg_file.replace('_seg.nii.gz', '.png')
    png_name = png_name.replace('Normal', '')
    png_file = os.path.join(cwd, png_name)
    im = Image.fromarray(img_data)
    im_90 = im.rotate(90)
    im_90.save(png_file)
    succ_dcm = succ_dcm + 1
    print(png_file)

#setup stop time
t1 = time.time()
total_time = t1-t0
hours = int(total_time/3600)
minutes = int((total_time - hours*3600)/60)
seconds = total_time - hours*3600 - minutes*60
print(f'Fetal brain segment took {hours:d}:{minutes:02d}:{seconds:.3f}')
print('Total:' + str(total_fbs) + ' Success:' + str(succ_dcm) + \
    ' Error:' + str(total_fbs - succ_dcm)) 
