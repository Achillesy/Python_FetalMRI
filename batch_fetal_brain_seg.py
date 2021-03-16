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
import sqlite3
from sqlite3.dbapi2 import Error
from orthanc_rest_client import Orthanc

if len(sys.argv) != 2:
    print("""
Batch process fetal_brain_seg.py according to series table. 

Usage: %s seg_CurrentDate
""" % (sys.argv[0]))
    exit(-1)

dbFile = "/mnt/Storage/Xuchu_Liu/orthanc/db-fetal/FetalMRIsqlite3.db"
orthancSrv = "http://localhost:8042"
orthanc_path = "/mnt/Storage/Xuchu_Liu/orthanc/db-v6/"

d2n = "dcm2niix -f "
para = ' -i y -l y -p y -x y -v y -z y -o '
output_path = "/mnt/Storage/Xuchu_Liu/Workspace/Python/FetalData/seg_20210309/"

seg = "python /mnt/Storage/Xuchu_Liu/Workspace/Python/NiftyMIC/MONAIfbs/monaifbs/fetal_brain_seg.py --input_names "

output_path = sys.argv[1]

# SELECT State == 1 GROUP BY PseudoAcc
def select_pseudoid_series(db_conn):
    table_select = f"""
            SELECT PseudoID, PseudoName, PseudoAcc
            FROM series WHERE State = 1
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
            FROM series WHERE State = 1
            AND PseudoID = ?;
        """
    try:
        select_rows = db_conn.cursor().execute(table_select, (PseudoId,)).fetchall()
        for row in select_rows:
            seriesnumber_dict[row[0]] = str(row[1]) + '_' + row[2] + '_' + str(row[3]) + 'x' + str(row[4])
    except Error as err:
        print('\033[1;35mSELECT', PseudoId, err, '. \033[0m')    

#UPDATE
def update_state_series(db_conn, seriesId) -> bool:
    table_update = f"""
            UPDATE series
            SET State = 2
            WHERE Id = ?;
        """
    try:
        db_conn.cursor().execute(table_update, (seriesId,))
        return True
    except Error as err:
        print('\033[1;35mUPDATE ', seriesId, err, '. \033[0m')
        return False

def mkdirs(path):
    if not os.path.exists(path):
        os.makedirs(path)        

##########
mkdirs(output_path)
conn = sqlite3.connect(dbFile)
orthanc = Orthanc(orthancSrv, warn_insecure=False)

# SELECT State == 1
pseudoid_dict = {}
select_pseudoid_series(conn)
for (key, value) in pseudoid_dict.items():
    # for each AccNumber
    acc_path = output_path + '/' + value
    mkdirs(acc_path)
    # for each SerialNumber of current PseudoId
    seriesnumber_dict = {}
    select_id_series(conn, key)
    for (skey, svalue) in seriesnumber_dict.items():
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
            if update_state_series(conn, skey):
                conn.commit()
            print(seg_file + " OK.")
        else:
            print('\033[1;35mCreate ', seg_file, ' error. \033[0m')

conn.close()
