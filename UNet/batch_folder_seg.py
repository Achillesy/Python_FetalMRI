#!/usr/bin/env python
#
# Instructions:
# Batch process batch_folder_seg.py by traverse folder.
#
# \author     Xuchu Liu (xuchu_liu@rush.edu)
# \date       08/16/2021
#

import os

curDir = os.walk('./')

d2n = "dcm2niix -f "
para = ' -a y -z y -o '

seg = "python /mnt/Storage/Xuchu_Liu/Workspace/Python/NiftyMIC/MONAIfbs/monaifbs/fetal_brain_seg.py --input_names "

series_list = list()
for path, dir_list, file_list in curDir:
    for file_name in file_list:
        if '.dcm' in file_name:
            series_list.append(path)
            break

sag_brain_list = list()
for series_Desc in series_list:
    series_lower = series_Desc.lower()
    # if ('brain' in series_lower) and ('sag' in series_lower):
    if ('sag' in series_lower):
        sag_brain_list.append(series_Desc)

for series_path in sag_brain_list:
    # './exam_000016/series004_SAG BrainT2 HASTE BH'
    svalue = series_path.split('/')[-1]
    svalue = svalue.split('_')[0]
    # convert *.dicom to SerialNumber_AX_HxW.nii.gz
    d2ncmd = d2n + svalue + para + '"' + series_path + '" "' + series_path + '" > /dev/null'
    print(d2ncmd)
    os.system(d2ncmd)

    nii_file = os.path.join(series_path, svalue + '.nii.gz')
    seg_file = os.path.join(series_path, svalue + '_seg.nii.gz')
    log_file = os.path.join(series_path, svalue + '_log.txt')
    if os.path.isfile(nii_file):
        segcmd = seg + '"' + nii_file + '" --segment_output_names "' + seg_file + '" > "' + log_file + '"'
        print(segcmd)
        os.system(segcmd)
    else:
        print('\033[1;35m', nii_file, ' does not exists. \033[0m')
    if os.path.isfile(seg_file):
        print(seg_file + " OK.")
    else:
        print('\033[1;35mCreate ', seg_file, ' error. \033[0m')
