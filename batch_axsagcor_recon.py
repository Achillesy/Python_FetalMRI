#!/usr/bin/env python
#
# Instructions:
# Batch process niftymic_run_reconstruction_pipeline.py according to last SeriesNumber. 
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
# \author     Xuchu Liu (xuchu_liu@rush.edu)
# \date       03/14/2021
#

import sys
import os
import sqlite3
from sqlite3.dbapi2 import Error

if len(sys.argv) != 2:
    print("""
Batch process niftymic_run_reconstruction_pipeline.py according to series table. 

Usage: %s seg_CurrentDate
""" % (sys.argv[0]))
    exit(-1)

dbFile = "/mnt/Storage/Xuchu_Liu/orthanc/db-fetal/FetalMRIsqlite3.db"

recon = "niftymic_run_reconstruction_pipeline --filenames "

# seg = "python /mnt/Storage/Xuchu_Liu/Workspace/Python/NiftyMIC/MONAIfbs/monaifbs/fetal_brain_seg.py --input_names "

input_path = sys.argv[1].rstrip('/')

# SELECT State == 2 GROUP BY PseudoAcc
def select_pseudoid_series(db_conn):
    table_select = f"""
            SELECT PseudoID, PseudoName, PseudoAcc
            FROM series WHERE State = 2
            GROUP BY PseudoAcc;
        """
    try: 
        select_rows = db_conn.cursor().execute(table_select).fetchall()
        for row in select_rows:
            pseudoid_dict[row[0]] = row[2] + '_' + str(row[1])
    except Error as err:
        print('\033[1;35mSELECT', err, '. \033[0m')

def select_id_series(db_conn, PseudoId):
    table_select = f"""
            SELECT Id, SeriesNumber, SeriesBrief, Height, Width
            FROM series WHERE State = 2
            AND PseudoID = ? ORDER BY SeriesNumber;
        """
    try:
        select_rows = db_conn.cursor().execute(table_select, (PseudoId,)).fetchall()
        for row in select_rows:
            seriesnumber_dict[row[0]] = str(row[1]) + '_' + row[2] + '_' + str(row[3]) + 'x' + str(row[4])
    except Error as err:
        print('\033[1;35mSELECT', PseudoId, err, '. \033[0m')    

# UPDATE
def update_state_series(db_conn, PseudoId, SeriesNumber, State) -> bool:
    table_update = f"""
            UPDATE series
            SET State = ?
            WHERE State = 2 AND PseudoId = ? AND SeriesNumber = ?;
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

# SELECT State == 2
pseudoid_dict = {}
select_pseudoid_series(conn)
total_recon = 0
succ_recon = 0
subject_recon = 0
preproc_recon = 0
for (key, value) in pseudoid_dict.items():
    # for each AccNumber
    filenames_ax = list()
    filenames_ax_masks = list()
    filenames_sag = list()
    filenames_sag_masks = list()
    filenames_cor = list()
    filenames_cor_masks = list()
    acc_path = input_path + '/' + value
    if not os.path.exists(acc_path):
        continue
    else:
        total_recon = total_recon + 1
        # for each SerialNumber of current PseudoId
        seriesnumber_dict = {}
        select_id_series(conn, key)
        for (skey, svalue) in seriesnumber_dict.items():
            series_path = acc_path + '/' + svalue
            if not os.path.exists(series_path):
                continue
            else:
                nii_path = series_path + '/nifti'
                nii_file = nii_path + '/' + svalue + '.nii.gz'
                seg_path = series_path + '/seg'
                seg_file = seg_path + '/' + svalue + '_seg.nii.gz'
                if os.path.isfile(nii_file) and os.path.isfile(seg_file):
                    if svalue.find("_AX_") > 0:
                        filenames_ax.append(str(nii_file))
                        filenames_ax_masks.append(str(seg_file))
                    if svalue.find("_SAG_") > 0:
                        filenames_sag.append(str(nii_file))
                        filenames_sag_masks.append(str(seg_file))
                    if svalue.find("_COR_") > 0:
                        filenames_cor.append(str(nii_file))
                        filenames_cor_masks.append(str(seg_file))
    # select the last ac/sag/cor
    if len(filenames_ax) < 1:
        print('\033[1;35mNo AX file error. \033[0m')
        continue
    if len(filenames_sag) < 1:
        print('\033[1;35mNo SAG file error. \033[0m')
        continue
    if len(filenames_cor) < 1:
        print('\033[1;35mNo COR file error. \033[0m')
        continue
    filenames = list()
    filenames.append(filenames_ax[-1])
    filenames.append(filenames_sag[-1])
    filenames.append(filenames_cor[-1])
    filenames_masks = list()
    filenames_masks.append(filenames_ax_masks[-1])
    filenames_masks.append(filenames_sag_masks[-1])
    filenames_masks.append(filenames_cor_masks[-1])
    # print(' '.join(map(str, filenames)))
    # print(' '.join(map(str, filenames_masks)))
    srr_path = acc_path + '/srr'
    log_file = acc_path + '/recon_log.txt'
    print("Waitng... niftymic_run_reconstruction_pipeline ")
    reconcmd = recon + ' '.join(map(str, filenames)) + \
        ' --filenames-masks ' + ' '.join(map(str, filenames_masks)) + \
        ' --dir-output ' + srr_path + ' | tee ' + log_file
    os.system(reconcmd)
    print("done!")
    recon_file = srr_path + '/recon_template_space/srr_template.nii.gz'
    if os.path.isfile(recon_file):
        for filename in filenames:
            origFile = filename.rsplit("/",1)[1]
            number = origFile.split("_",1)[0]
            update_state_series(conn, key, number, '3')
        conn.commit()
        succ_recon = succ_recon + 1
        print(recon_file + " OK.")
    elif os.path.exists(srr_path + "/recon_subject_space"):
        for filename in filenames:
            origFile = filename.rsplit("/",1)[1]
            number = origFile.split("_",1)[0]
            update_state_series(conn, key, number, '4')
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

print('Total:' + str(total_recon) + ' Success:' + str(succ_recon) + \
    ' noTemplate:' + str(subject_recon) + ' noSubject:' + str(preproc_recon)) 
conn.close()
