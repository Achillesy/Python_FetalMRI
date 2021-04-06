#!/usr/bin/env python
#
# Instructions:
# Batch process niftymic_run_reconstruction_pipeline.py according to series table. 
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
# \date       03/11/2021
#

import sys
import os
import time
import sqlite3
from sqlite3.dbapi2 import Error
import nibabel as nib
import numpy as np

if len(sys.argv) < 3:
    print("""
Batch process niftymic_run_reconstruction_pipeline.py according to series table. 

Usage: %s fetal_brain_seg CurrentDate_srr [arguments...]
""" % (sys.argv[0]))
    exit(-1)

dbFile = "FetalMRIsqlite3.db"

recon = "niftymic_run_reconstruction_pipeline --filenames "

input_path = sys.argv[1].rstrip('/')
output_path = sys.argv[2].rstrip('/')
arguments = ' '.join(sys.argv[3:])

#setup start time
t0 = time.time()

# SELECT State == 3 GROUP BY PseudoAcc
def select_pseudoid_series(db_conn):
    table_select = f"""
            SELECT PseudoID, PseudoName, PseudoAcc
            FROM series WHERE State = 3
            GROUP BY PseudoAcc;
        """
    try: 
        select_rows = db_conn.cursor().execute(table_select).fetchall()
        for row in select_rows:
            pseudoid_dict[row[0]] = row[2] + '_' + str(row[1])
    except Error as err:
        print('\033[1;35mSELECT', err, '. \033[0m')

def select_id_series(db_conn, PseudoId, State):
    table_select = f"""
            SELECT Id, SeriesNumber, SeriesBrief, Height, Width, SegCount
            FROM series WHERE State = ?
            AND PseudoID = ? ORDER BY SeriesNumber;
        """
    try:
        select_rows = db_conn.cursor().execute(table_select, (State, PseudoId)).fetchall()
        for row in select_rows:
            seriesnumber_dict[row[0]] = str(row[5]) + '_' + str(row[1]) + '_' + row[2] + \
                '_' + str(row[3]) + 'x' + str(row[4])
    except Error as err:
        print('\033[1;35mSELECT', PseudoId, err, '. \033[0m')    

# UPDATE
def update_state_series(db_conn, PseudoId, SeriesNumber, State) -> bool:
    table_update = f"""
            UPDATE series
            SET State = ?
            WHERE (State = 3 OR State = 9) AND PseudoId = ? AND SeriesNumber = ?;
        """
    try:
        db_conn.cursor().execute(table_update, (State, PseudoId, SeriesNumber))
        return True
    except Error as err:
        print('\033[1;35mUPDATE ', PseudoId, err, '. \033[0m')
        return False

def mkdirs(path):
    if not os.path.exists(path):
        os.makedirs(path)     
 
##########
conn = sqlite3.connect(dbFile)

# SELECT State == 3
pseudoid_dict = {}
select_pseudoid_series(conn)
total_recon = 0
succ_recon = 0
subject_recon = 0
preproc_recon = 0
target_arg = ''
for (key, value) in pseudoid_dict.items():
    # for each AccNumber
    filenames = list()
    filenames_masks = list()
    acc_path = input_path + '/' + value
    if not os.path.exists(acc_path):
        continue
    else:
        total_recon = total_recon + 1
        # for each SerialNumber of current PseudoId
        seriesnumber_dict = {}
        select_id_series(conn, key, '3')
        maxCount = 0
        target_arg = ''
        for (skey, svalue) in seriesnumber_dict.items():
            [sCount, sName] = svalue.split('_', 1)
            series_path = acc_path + '/' + sName
            if not os.path.exists(series_path):
                continue
            else:
                nii_path = series_path + '/nifti'
                nii_file = nii_path + '/' + sName + '.nii.gz'
                seg_path = series_path + '/seg'
                seg_file = seg_path + '/' + sName + '_seg.nii.gz'
                if os.path.isfile(nii_file) and os.path.isfile(seg_file):
                    filenames.append(str(nii_file))
                    filenames_masks.append(str(seg_file))
                    tempCount = int(sCount)
                    if tempCount > maxCount:
                        maxCount = tempCount
                        target_arg = ' --target-stack ' + str(nii_file)
        # seriesnumber_dict = {}
        # select_id_series(conn, key, '9')
        # for (skey, svalue) in seriesnumber_dict.items():
        #     series_path = acc_path + '/' + svalue
        #     if not os.path.exists(series_path):
        #         continue
        #     else:
        #         nii_path = series_path + '/nifti'
        #         target_file = nii_path + '/' + svalue + '.nii.gz'
        #         seg_path = series_path + '/seg'
        #         seg_file = seg_path + '/' + svalue + '_seg.nii.gz'
        #         if os.path.isfile(target_file) and os.path.isfile(seg_file):
        #             filenames.append(str(target_file))
        #             filenames_masks.append(str(seg_file))
        #             arguments = arguments + ' --target-stack ' + str(target_file)
    # print(' '.join(map(str, filenames)))
    # print(' '.join(map(str, filenames_masks)))
    mkdirs(output_path)
    srr_path = output_path + '/' + value
    mkdirs(srr_path)
    log_file = srr_path + '/' + value + '_log.txt'
    print("Waitng... niftymic_run_reconstruction_pipeline ")
    reconcmd = recon + ' '.join(map(str, filenames)) + \
        ' --filenames-masks ' + ' '.join(map(str, filenames_masks)) + \
        ' --dir-output ' + srr_path + target_arg + ' ' + arguments + \
        ' 2>&1 | tee ' + log_file
    # print(reconcmd) #Debug
    os.system(reconcmd)
    print("done!")
    recon_file = srr_path + '/recon_template_space/srr_template.nii.gz'
    if os.path.isfile(recon_file):
        for filename in filenames:
            origFile = filename.rsplit("/",1)[1]
            number = origFile.split("_",1)[0]
            update_state_series(conn, key, number, '4')
        conn.commit()
        succ_recon = succ_recon + 1
        os.system('mv ' + recon_file + ' ' + output_path + '/' + value + '_srr.nii.gz')
        print(recon_file + " OK.")
    elif os.path.exists(srr_path + "/recon_subject_space"):
        for filename in filenames:
            origFile = filename.rsplit("/",1)[1]
            number = origFile.split("_",1)[0]
            update_state_series(conn, key, number, '6')
        conn.commit()
        subject_recon = subject_recon + 1
        print('\033[1;35mCreate template ', recon_file, ' error. \033[0m')
    else:
        for filename in filenames:
            origFile = filename.rsplit("/",1)[1]
            number = origFile.split("_",1)[0]
            update_state_series(conn, key, number, '5')
        conn.commit()
        preproc_recon = preproc_recon + 1
        print('\033[1;35mCreate subject ', recon_file, ' error. \033[0m')


    # if os.path.exists(srr_path + "/recon_subject_space"):
    #     subject_path = srr_path + '/recon_subject_space/'
    #     subject_file = subject_path + 'srr_subject.nii.gz'
    #     mask_file = subject_path + 'srr_subject_mask.nii.gz'
    #     if os.path.isfile(subject_file) and os.path.isfile(mask_file):
    #         subject_img = nib.load(subject_file)
    #         subject_img_data = subject_img.get_fdata()
    #         mask_img = nib.load(mask_file)
    #         mask_img_data = mask_img.get_fdata()
    #         fetal_img_data = subject_img_data * mask_img_data
    #         fetal_img = nib.Nifti1Pair(fetal_img_data, np.eye(4))
    #         fetal_file = output_path + '/' + value + '_subject.nii.gz'
    #         nib.save(fetal_img, fetal_file)

conn.close()

#setup stop time
t1 = time.time()
total_time = t1-t0
hours = int(total_time/3600)
minutes = int((total_time - hours*3600)/60)
seconds = total_time - hours*3600 - minutes*60
print(f'Reconstruction took {hours:d}:{minutes:02d}:{seconds:.3f}')
print('Total:' + str(total_recon) + ' Success:' + str(succ_recon) + \
    ' noTemplate:' + str(subject_recon) + ' noSubject:' + str(preproc_recon)) 
