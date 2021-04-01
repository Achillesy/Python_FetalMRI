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
# from orthanc_rest_client import Orthanc
# import imageio

if len(sys.argv) != 3:
    print("""
Batch process fetal_brain_seg.py according to series table. 

Usage: %s monaifbs_seg CurrentDate_dcm
""" % (sys.argv[0]))
    exit(-1)

dbFile = "FetalMRIsqlite3.db"

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
        dcm_path = monaifbs_series_path + '/dcm'
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
                nii_img = nib.load(nii_file)
                nii_img_data = nii_img.get_fdata()
                brain_img_data = nii_img_data * seg_img_data[:,:,:,0]
                (L, W, S) = brain_img_data.shape
                TH100 = L*W/100
                for s in range(S):
                    brain_slice = brain_img_data[:,:,s]
                    if np.count_nonzero(brain_slice) > TH100:
                        # TODO save dcm

                        seg_count = seg_count + 1
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




        # os.system("find " + dcm_path + " -type l -delete")
        # insts = orthanc.get_series_instances(skey)
        # for inst in insts:
        #     fileUUID = inst['FileUuid']
        #     raw_file = orthanc_path + fileUUID[0:2] + '/' + fileUUID[2:4] + '/' + fileUUID
        #     os.system("ln -s " + raw_file + ' ' + dcm_path + '/')
        #     print('.', end='')
        # print("done!")

        # seg_path = series_path + '/seg'
        # mkdirs(seg_path)
        # nii_file = nii_path + '/' + svalue + '.nii.gz'
        # seg_file = seg_path + '/' + svalue + '_seg.nii.gz'
        # log_file = seg_path + '/' + svalue + '_log.txt'
        # print("Waitng... fetal_brain_seg ")
        # if os.path.isfile(nii_file):
        #     segcmd = seg + nii_file + " --segment_output_names " + seg_file + " > " + log_file
        #     os.system(segcmd)
        #     print("done!")
        # else:
        #     print('\033[1;35m', nii_file, ' does not exists. \033[0m')

        # if os.path.isfile(seg_file):
        #     seg_img = nib.load(seg_file)
        #     seg_img_data = seg_img.get_fdata()
        #     # seg_img_size = len(np.nonzero(seg_img_data)[0])
        #     seg_img_size = np.count_nonzero(seg_img_data)
        #     if seg_img_size > 0:
        #         nii_img = nib.load(nii_file)
        #         nii_img_data = nii_img.get_fdata()
        #         brain_img_data = nii_img_data * seg_img_data[:,:,:,0]
        #         (L, W, S) = brain_img_data.shape
        #         TH100 = L*W/100
        #         # TH16 = L*W/16
        #         # TH9 = L*W/9
        #         Sel = '2'
        #         for s in range(S):
        #             brain_slice = brain_img_data[:,:,s]
        #             if np.count_nonzero(brain_slice) > TH100:
        #                 # Sel = '3'
        #                 if 'AX' in svalue:
        #                     imageio.imwrite(acc_ax_path + '/' + svalue + '_' + str(s) + '.png', brain_slice)
        #                 elif 'SAG' in svalue:
        #                     imageio.imwrite(acc_sag_path + '/' + svalue + '_' + str(s) + '.png', brain_slice)
        #                 else:
        #                     imageio.imwrite(acc_cor_path + '/' + svalue + '_' + str(s) + '.png', brain_slice)
        #             # if np.count_nonzero(brain_slice) > TH9:
        #             #     Sel = '9'
        #         print(seg_file + " OK.")
        #         succ_fbs = succ_fbs + 1
        #         conn.update_series_state(skey, seg_img_size, Sel)
        #     else:
        #         conn.update_series_state(skey, seg_img_size, '0')
        # else:
        #     print('\033[1;35mCreate ', seg_file, ' error. \033[0m')

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
