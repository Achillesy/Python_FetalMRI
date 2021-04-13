#!/usr/bin/env python
#
# Instructions:
# Batch process fetal_brain_dcm.py according to series table. 
# CurrentDate_dcm
#   |__PseudoAcc_PseudoName
#   |    |__SeriesNumber_AX_HeightxWidth
#   |    |__SeriesNumber_COR_HeightxWidth
#   |    |__SeriesNumber_SAG_HeightxWidth
#   |__PseudoAcc_PseudoName
#
# \author     Xuchu Liu (xuchu_liu@rush.edu)
# \date       04/01/2021
#

import sys
import os
import numpy as np
import time
import fetaldb
import nibabel as nib
from orthanc_rest_client import Orthanc
import pydicom
import uuid

if len(sys.argv) != 3:
    print("""
Batch process fetal_brain_seg.py according to series table. 

Usage: %s monaifbs_seg CurrentDate_dcm
""" % (sys.argv[0]))
    exit(-1)

dbFile = "FetalMRIsqlite3.db"
orthancSrv = "http://localhost:8042"
orthanc_path = "/mnt/Storage/Xuchu_Liu/orthanc/db-v6/"

monaifbs_path = sys.argv[1].rstrip('/')
output_dcm_path = sys.argv[2].rstrip('/')

#setup start time
t0 = time.time()

def mkdirs(path):
    if not os.path.exists(path):
        os.makedirs(path)        

##########
mkdirs(output_dcm_path)
conn = fetaldb.FetalDB(dbFile)
orthanc = Orthanc(orthancSrv, warn_insecure=False)

# SELECT State == 1
total_fbs = 0
succ_dcm = 0
pseudoid_dict = conn.select_series_pseudoid('3')
for (key, value) in pseudoid_dict.items():
    # for each AccNumber
    monaifbs_acc_path = monaifbs_path + '/' + value
    output_acc_path = output_dcm_path + '/' + value
    mkdirs(output_acc_path)
    # for each SerialNumber of current PseudoId
    seriesnumber_dict = conn.select_series_id(key, '3')
    for (skey, svalue) in seriesnumber_dict.items():
        total_fbs = total_fbs + 1
        monaifbs_series_path = monaifbs_acc_path + '/' + svalue
        output_series_path = output_acc_path + '/' + svalue
        mkdirs(output_series_path)
        nii_path = monaifbs_series_path + '/nifti'
        seg_path = monaifbs_series_path + '/seg'
        nii_file = nii_path + '/' + svalue + '.nii.gz'
        seg_file = seg_path + '/' + svalue + '_seg.nii.gz'
        seg_count = 0
        if os.path.isfile(nii_file) and os.path.isfile(seg_file):
            seg_img = nib.load(seg_file)
            seg_img_data = seg_img.get_fdata()
            # seg_img_size = len(np.nonzero(seg_img_data)[0])
            seg_img_size = np.count_nonzero(seg_img_data)
            if seg_img_size > 0:
                # Extended border Start
                board = np.nonzero(seg_img_data)
                (X, Y, Z, Tmp) = seg_img_data.shape
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
                seg_img_data[minX:maxX+1, minY:maxY+1, minZ:maxZ+1, :] = 1
                # Extended border End
                nii_img = nib.load(nii_file)
                nii_img_data = nii_img.get_fdata()
                brain_img_data = nii_img_data * seg_img_data[:,:,:,0]
                (L, W, S) = brain_img_data.shape
                TH100 = L*W/100
                insts = orthanc.get_series_instances(skey)
                for s in range(S):
                    brain_slice = brain_img_data[:,:,s]
                    if np.count_nonzero(brain_slice) > TH100:
                        # TODO save dcm
                        seg_count = seg_count + 1
                        brain_slice = brain_slice.T
                        brain_slice = brain_slice[::-1]
                        for inst in insts:
                            if s == (S - inst['IndexInSeries']):
                                fileUUID = inst['FileUuid']
                                raw_file = orthanc_path + fileUUID[0:2] + '/' + fileUUID[2:4] + '/' + fileUUID
                                ds = pydicom.dcmread(raw_file)
                                PatientName = str(ds.PatientName) + '_seg'
                                ds.PatientName = PatientName
                                ds.PatientID = str(uuid.uuid3(uuid.NAMESPACE_DNS, PatientName))
                                arr = ds.pixel_array
                                arr[:,:] = brain_slice[:,:]
                                ds.PixelData = arr.tobytes()
                                dcm_file = output_series_path + '/' + str(inst['IndexInSeries']) + '.dcm'
                                ds.save_as(dcm_file)
                if seg_count > 0:
                    print(seg_file + " OK.")
                    succ_dcm = succ_dcm + 1
                    conn.update_series_segcount(skey, seg_count)
                else:
                    print(seg_file + " count=0.")
                    conn.update_series_state(skey, '2')
            else: # end if seg_img_size > 0
                print(seg_file + " size=0.")
                conn.update_series_state(skey, '0')
conn.close()

#setup stop time
t1 = time.time()
total_time = t1-t0
hours = int(total_time/3600)
minutes = int((total_time - hours*3600)/60)
seconds = total_time - hours*3600 - minutes*60
print(f'Fetal brain segment took {hours:d}:{minutes:02d}:{seconds:.3f}')
print('Total:' + str(total_fbs) + ' Success:' + str(succ_dcm) + \
    ' Error:' + str(total_fbs - succ_dcm)) 
