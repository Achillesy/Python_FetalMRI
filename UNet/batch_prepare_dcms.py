#!/usr/bin/env python
#
# Instructions:
# Batch process batch_prepare_dcms.py to prepare dicom files for mark.
#
# \author     Xuchu Liu (xuchu_liu@rush.edu)
# \date       08/16/2021
#

import os
import numpy as np
import pydicom
from PIL import Image

import nibabel as nib

def normalization(data):
    _range = np.max(data) - np.min(data)
    return (data - np.min(data)) / _range

curDir = os.getcwd()
curFolder = os.walk(curDir)

dcmfile_list = list()
for path, dir_list, file_list in curFolder:
    for file_name in file_list:
        if '_seg.nii.gz' in file_name:
            # Find the top 3 segmentation size
            seg_file = os.path.join(path, file_name)
            seg_img = nib.load(seg_file)
            seg_img_data = seg_img.get_fdata()
            seg_img_size = np.count_nonzero(seg_img_data)
            if seg_img_size > 0:
                (X, Y, Z, Tmp) = seg_img_data.shape
                size_list  = list()
                for z in range(Z):
                    size = np.count_nonzero(seg_img_data[:,:,z,0])
                    size_list.append(-size)
                size_list.reverse()
                index = np.argsort(size_list)

                board = np.nonzero(seg_img_data)
                X = X - 1
                Y = Y - 1
                minX, maxX = min(board[0])-10, max(board[0])+10
                if minX < 0:
                    minX = 0
                if maxX > X:
                    maxX = X
                minY, maxY = min(board[1])-10, max(board[1])+10
                if minY < 0:
                    minY = 0
                if maxY > Y:
                    maxY = Y
                minZ, maxZ = min(board[2]), max(board[2])
                SegCount = maxZ - minZ + 1
                SegX = minX
                SegWidth = maxX - minX + 1
                SegY = Y - maxY
                SegHeight = maxY - minY + 1
                SelFrom = min(index[0:3])
                SelTo = max(index[0:3])
                json_txt = '{{"SegX":{},"SegWidth":{},"SegY":{},"SegHeight":{},"SegCount":{}, "SelFrom":{}, "SelTo":{}}}' \
                    .format(SegX, SegWidth, SegY, SegHeight, SegCount, SelFrom+1, SelTo+1)
                print(json_txt)
                json_file = seg_file.replace('_seg.nii.gz', '_seg_info.json')
                with open(json_file, 'w') as jf:
                    jf.write(json_txt)
                
                for idx in range(SelFrom, SelTo+1):
                    if size_list[idx] < 0:
                        series_num = '%04d' % (idx+1)
                        for file_name in file_list:
                            if (series_num in file_name) and ('.dcm' in file_name):
                                dcm_file = os.path.join(path, file_name)
                                dcmfile_list.append(dcm_file)
                                print(dcm_file)
                                try:
                                    ds = pydicom.dcmread(dcm_file, force=True)
                                    raw_img = ds.pixel_array
                                    maxSide = max(SegWidth, SegHeight)
                                    jpg_img = np.zeros((maxSide, maxSide))
                                    jpg_img[0:SegHeight-1, 0:SegWidth-1] = raw_img[SegY:(SegY+SegHeight-1), SegX:(SegX+SegWidth-1)]
                                    new_jpg = Image.fromarray(normalization(jpg_img)*255).convert('L')
                                    # new_jpg = Image.fromarray(normalization(raw_img)*255).convert('L')
                                    accession = ds.AccessionNumber
                                    series = str(ds.SeriesNumber)
                                    instance = str(ds.InstanceNumber)
                                    jpg_sag_name = '%s_%s_%s_SAG.jpg' % (accession, series, instance)
                                    new_jpg.save(jpg_sag_name, 'jpeg')
                                except  Exception as e:
                                    print('Exception Reson:', e)
                                    pass
                                break

fileOject = open('dcmfileList.txt', 'w')
for dcm_file in dcmfile_list:
    fileOject.write(dcm_file)
    fileOject.write('\n')
fileOject.close()
