#!/usr/bin/env python
#
# Instructions:
# Get current XXX_seg.nii.gz info and write to XXX_seg_info.json.
# {"SegX":1,"SegWidth":20,"SegY":1,"SegHeight":20,"SegCount":1}
#
# \author     Xuchu Liu (xuchu_liu@rush.edu)
# \date       07/21/2021
#

# import sys
import os
import numpy as np
import nibabel as nib
# import pydicom
# import uuid

allfilelist = os.listdir('.')
for f in allfilelist:
    if '_seg.nii.gz' in f:
        seg_file = f
        seg_img = nib.load(seg_file)
        seg_img_data = seg_img.get_fdata()
      # seg_img_size = len(np.nonzero(seg_img_data)[0])
        seg_img_size = np.count_nonzero(seg_img_data)
        if seg_img_size > 0:
            # Extended border Start
            board = np.nonzero(seg_img_data)
            (X, Y, Z, Tmp) = seg_img_data.shape
            X = X - 1
            Y = Y - 1
            minX, maxX = min(board[0])-10, max(board[0])+10
            minY, maxY = min(board[1])-10, max(board[1])+10
            minZ, maxZ = min(board[2]), max(board[2])
            if minX<0:
                minX = 0
            if maxX>X:
                maxX = X
            if minY<0:
                minY = 0
            if maxY>Y:
                maxY = Y
            # print(X, Y, Z, Tmp, minX, maxX, minY, maxY, minZ, maxZ)
            SegCount = maxZ - minZ + 1
            SegX = minX + 1
            SegWidth = maxX - minX + 1
            SegY = Y - maxY
            SegHeight = maxY - minY + 1
            json_txt = '{{"SegX":{},"SegWidth":{},"SegY":{},"SegHeight":{},"SegCount":{}}}'.format(SegX, SegWidth, SegY, SegHeight, SegCount)
            print(json_txt)
            json_file = seg_file.replace('_seg.nii.gz', '_seg.json')
            with open(json_file, 'w') as jf:
                jf.write(json_txt)
