#!/usr/bin/env python
#
# Instructions:
# Batch process fetal_brain_seg.py according to series table. 
# seg_CurrentDate
#   |__PseudoAcc_PseudoName
#   |    |__SeriesNumber_AX_HeightxWidth
#   |    |   |__dcm
#   |    |   |__nifti
#   |    |   |__seg
#   |    |__SeriesNumber_COR_HeightxWidth
#   |    |__SeriesNumber_SAG_HeightxWidth
#   |    |__srr
#   |__PseudoAcc_PseudoName
#
# \author     Xuchu Liu (xuchu_liu@rush.edu)
# \date       03/11/2021
#

import sys
import os
import time
import fetaldb
from orthanc_rest_client import Orthanc

if len(sys.argv) != 2:
    print("""
Batch process fetal_brain_seg.py according to series table. 

Usage: %s seg_CurrentDate
""" % (sys.argv[0]))
    exit(-1)

dbFile = "FetalMRIsqlite3.db"
orthancSrv = "http://localhost:8042"
orthanc_path = "/mnt/Storage/Xuchu_Liu/orthanc/db-v6/"

d2n = "dcm2niix -f "
para = ' -i y -l y -p y -x y -v y -z y -o '

seg = "python /mnt/Storage/Xuchu_Liu/Workspace/Python/NiftyMIC/MONAIfbs/monaifbs/fetal_brain_seg.py --input_names "

output_path = sys.argv[1].rstrip('/')

#setup start time
t0 = time.time()

def mkdirs(path):
    if not os.path.exists(path):
        os.makedirs(path)        

##########
mkdirs(output_path)
conn = fetaldb.FetalDB(dbFile)
orthanc = Orthanc(orthancSrv, warn_insecure=False)

# SELECT State == 1
total_fbs = 0
succ_fbs = 0
pseudoid_dict = conn.select_series_pseudoid('1')
for (key, value) in pseudoid_dict.items():
    # for each AccNumber
    acc_path = output_path + '/' + value
    mkdirs(acc_path)
    # for each SerialNumber of current PseudoId
    seriesnumber_dict = conn.select_series_id(key, '1')
    for (skey, svalue) in seriesnumber_dict.items():
        total_fbs = total_fbs + 1
        series_path = acc_path + '/' + svalue
        mkdirs(series_path)
        dcm_path = series_path + '/dcm'
        mkdirs(dcm_path)
        nii_path = series_path + '/nifti'
        mkdirs(nii_path)
        os.system("find " + dcm_path + " -type l -delete")
        insts = orthanc.get_series_instances(skey)
        for inst in insts:
            fileUUID = inst['FileUuid']
            raw_file = orthanc_path + fileUUID[0:2] + '/' + fileUUID[2:4] + '/' + fileUUID
            os.system("ln -s " + raw_file + ' ' + dcm_path + '/')
            print('.', end='')
        print("done!")
        # convert *.dicom to SerialNumber_AX_HxW.nii.gz
        print("Waitng... dcm2niix ")
        d2ncmd = d2n + svalue + para + nii_path + ' ' + dcm_path + ' > /dev/null'
        os.system(d2ncmd)
        print("done!")
        seg_path = series_path + '/seg'
        mkdirs(seg_path)
        nii_file = nii_path + '/' + svalue + '.nii.gz'
        seg_file = seg_path + '/' + svalue + '_seg.nii.gz'
        log_file = seg_path + '/' + svalue + '_log.txt'
        print("Waitng... fetal_brain_seg ")
        if os.path.isfile(nii_file):
            segcmd = seg + nii_file + " --segment_output_names " + seg_file + " > " + log_file
            os.system(segcmd)
            print("done!")
        else:
            print('\033[1;35m', nii_file, ' does not exists. \033[0m')
        if os.path.isfile(seg_file):
            conn.update_series_state(skey, '2')
            succ_fbs = succ_fbs + 1
            print(seg_file + " OK.")
        else:
            print('\033[1;35mCreate ', seg_file, ' error. \033[0m')

conn.close()

#setup stop time
t1 = time.time()
total_time = t1-t0
hours = int(total_time/3600)
minutes = int((total_time - hours*3600)/60)
seconds = total_time - hours*3600 - minutes*60
print(f'Fetal brain segment took {hours:d}:{minutes:02d}:{seconds:.3f}')
print('Total:' + str(total_fbs) + ' Success:' + str(succ_fbs) + \
    ' Error:' + str(total_fbs - succ_fbs)) 
