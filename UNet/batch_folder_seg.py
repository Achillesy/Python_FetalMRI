#!/usr/bin/env python
#
# Instructions:
# Batch process batch_folder_seg.py by traverse folder.
#
# \author     Xuchu Liu (xuchu_liu@rush.edu)
# \date       08/16/2021
#

import os
import json
import uuid

import numpy as np
import nibabel as nib
import pydicom

curDir = os.walk('./')

d2n = "dcm2niix -f "
para = ' -i y -x y -m y -v y -z y -o '

seg = "python /mnt/Storage/Xuchu_Liu/Workspace/Python/NiftyMIC/MONAIfbs/monaifbs/fetal_brain_seg.py --input_names "

series_list = list()
for path, dir_list, file_list in curDir:
    for file_name in file_list:
        if '.dcm' in file_name:
            series_list.append(path)
            break

sag_brain_list = list()
for series_Desc in series_list:
    series_upper = series_Desc.upper()
    # if ('brain' in series_upper) and ('sag' in series_upper):
    if ('AX' in series_upper):
        sag_brain_list.append(series_Desc)

for series_path in sag_brain_list:
    # './exam_000016/series004_SAG BrainT2 HASTE BH'
    dcm_list = os.listdir(series_path)
    dcm_list = list(filter(lambda x: '.dcm' in x, dcm_list))
    dcm_list.sort()
    dcm_first = os.path.join(series_path, dcm_list[0])
    ds_first = pydicom.dcmread(dcm_first, force=True)
    accession = ds_first.AccessionNumber
    series = '%02d' % (ds_first.SeriesNumber)
    seriesName = accession + '_' + series
    svalue = seriesName
    # convert *.dicom to ACC_Serial.nii.gz
    d2ncmd = d2n + svalue + para + '"' + series_path + '" "' + series_path + '" > /dev/null'
    print(d2ncmd)
    os.system(d2ncmd)

    nii_file = os.path.join(series_path, svalue + '.nii.gz')
    seg_file = os.path.join(series_path, svalue + '_pos_seg.nii.gz')
    log_file = os.path.join(series_path, svalue + '_pos_log.txt')
    if os.path.isfile(nii_file):
        nii_img = nib.load(nii_file)
        nii_img_data = nii_img.get_fdata()
        # nii_img_data = np.squeeze(nii_img_data)
        if nii_img_data.ndim > 3:
            nii_img_data_0 = nii_img.slicer[:,:,:,0]
            nii_file = os.path.join(series_path, svalue + '_0.nii.gz')
            nii_img_data_0.to_filename(nii_file)
            nii_img_data = nii_img_data[:,:,:,0]
        nii_first_img = nii_img_data[:,:,0]
        nii_first_img_90 = np.rot90(nii_first_img)
        # print(nii_first_img_90)
        # print(ds_first.pixel_array)
        if ~(nii_first_img_90 == ds_first.pixel_array).all():
            dcm_list.reverse()
            seg_file = seg_file.replace('_pos', '_rev')
            log_file = log_file.replace('_pos', '_rev')
        segcmd = seg + '"' + nii_file + '" --segment_output_names "' + seg_file + '" > "' + log_file + '"'
        print(segcmd)
        os.system(segcmd)
    else:
        print('\033[1;35m', nii_file, ' does not exists. \033[0m')
    
    if os.path.isfile(seg_file):
        seg_img = nib.load(seg_file)
        seg_img_data = seg_img.get_fdata()
        seg_img_size = np.count_nonzero(seg_img_data)
        if seg_img_size > 0:
            # Extended border Start
            print(seg_file + " OK.")
            # seg_img_data = np.squeeze(seg_img_data)
            X, Y, Z, D = seg_img_data.shape
            # print(X, Y, Z, D)
            X = X - 1
            Y = Y - 1
            txt = {}
            # txt['PseudoAcc'] = accession
            # txt['SeriesNumber'] = series
            for i in range(Z):
                seg_img_size_cur = np.count_nonzero(seg_img_data[:,:,i])
                if seg_img_size_cur > 0:
                    dcm_cur = os.path.join(series_path, dcm_list[i])
                    ds_cur = pydicom.dcmread(dcm_cur, force=True)
                    instance = '%02d' % (ds_cur.InstanceNumber)
                    instanceName = seriesName + '_' + instance
                    Id = str(uuid.uuid3(uuid.NAMESPACE_DNS, instanceName))
                    txt[Id] = {}
                    board = np.nonzero(seg_img_data[:,:,i])
                    minX, maxX = min(board[0]), max(board[0])
                    minY, maxY = min(board[1]), max(board[1])
                    SegX = minX
                    SegWidth = maxX - minX + 1
                    SegY = Y - maxY
                    SegHeight = maxY - minY + 1
                    txt[Id]['SegX'] = int(SegX)
                    txt[Id]['SegWidth'] = int(SegWidth)
                    txt[Id]['SegY'] = int(SegY)
                    txt[Id]['SegHeight'] = int(SegHeight)
            json_code = json.dumps(txt)
            json_file = seg_file.replace('_seg.nii.gz', '_seg_info.json')
            with open(json_file, 'w') as jf:
                jf.write(json_code)
            print(json_code)
        else:
            print('\033[1;The ', seg_file, ' has zero size. \033[0m')
    else:
        print('\033[1;35mCreate ', seg_file, ' error. \033[0m')
