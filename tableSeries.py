#!/usr/bin/env python

#
# Instructions:
# 1. Sqlite3 DB: FetalMRIsqlite3.db
# 2. Table:      series
# CREATE TABLE "series" (
# 	"Id"	TEXT,
# 	"SeriesDescription"	TEXT,
# 	"SeriesNumber"	INTEGER,
# 	"PseudoID"	TEXT,
# 	"PseudoName"	TEXT,
# 	"PseudoAcc"	TEXT,
# 	"Stats"	INTEGER DEFAULT 0,
# 	PRIMARY KEY("Id")
# );
#
# State:
#   0: insert serial info
#   1: update serial info
#
# \author     Xuchu Liu (xuchu_liu@rush.edu)
# \date       03/08/2021
#
import sys
import os
import re
import sqlite3
from sqlite3.dbapi2 import Error
from orthanc_rest_client import Orthanc

dbFile = "FetalMRIsqlite3.db"
orthancSrv = "http://localhost:8042"
orthanc_path = "/mnt/Storage/Xuchu_Liu/orthanc/db-v6/"

d2n = "dcm2niix -f "
para = ' -i y -l y -p y -x y -v y -z y -o '
output_path = "/mnt/Storage/Xuchu_Liu/Workspace/Python/FetalData/seg_20210309/"

seg = "python /mnt/Storage/Xuchu_Liu/Workspace/Python/NiftyMIC/MONAIfbs/monaifbs/fetal_brain_seg.py --input_names "

# Insert
def insert_series(db_conn, seriesId, SeriesDescription, SeriesDate, SeriesNumber, PseudoID, PseudoName, PseudoAcc, State) -> bool:
    table_insert = f"""
            INSERT INTO series (Id, SeriesDescription, SeriesDate, SeriesNumber, PseudoID, PseudoName, PseudoAcc, State)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """
    try:
        db_conn.cursor().execute(table_insert, (seriesId, SeriesDescription, SeriesDate, SeriesNumber, PseudoID, PseudoName, PseudoAcc, State))
        return True
    except Error as err:
        print('\033[1;35mINSERT', seriesId, err, '. \033[0m')
        return False

def insert_info_to_series():
    all_series = orthanc.get_series()
    seriesNew = 0
    for series in all_series:
        #info = orthanc.get_one_series(series)
        # SeriesDescription = ''
        # State = 0
        # if info['MainDicomTags'].get('SeriesDescription'):
        #     SeriesDescription = info['MainDicomTags']['SeriesDescription']
        #     if bool(re.search('(?=.*HASTE)(?=.*T2)(?=.*BRAIN)(?=.*(SAG|AX|COR))', SeriesDescription, re.IGNORECASE)):
        #         State = 1
        # SeriesNumber = info['MainDicomTags']['SeriesNumber']
        # SeriesDate = info['MainDicomTags']['SeriesDate']
        # study = orthanc.get_series_study(series)
        # PseudoID = study['PatientMainDicomTags']['PatientID']
        # PseudoName = study['PatientMainDicomTags']['PatientName']
        # PseudoAcc = study['MainDicomTags']['AccessionNumber']
        info = orthanc.get_series_shared_tags(series)
        SeriesDescription = ''
        State = 0
        if '0008,103e' in info:
            SeriesDescription = info['0008,103e']['Value']
            if bool(re.search('(?=.*HASTE)(?=.*T2)(?=.*BRAIN)(?=.*(SAG|AX|COR))', SeriesDescription, re.IGNORECASE)):
                State = 1
        SeriesDate = ''
        if '0008,0021' in info:
            SeriesDate = info['0008,0021']['Value']
        elif '0008,0012' in info:
            SeriesDate = info['0008,0012']['Value']
        SeriesNumber = info['0020,0011']['Value']
        PseudoID = info['0010,0020']['Value']
        PseudoName = info['0010,0010']['Value']
        PseudoAcc = info['0008,0050']['Value']
        if insert_series(conn, series, SeriesDescription, SeriesDate, SeriesNumber, PseudoID, PseudoName, PseudoAcc, State):
            print('INSERT ', PseudoName, PseudoAcc, SeriesDate, SeriesNumber, ' success.')
            seriesNew += 1
    print('Total of ' + str(seriesNew) + ' series INSERT success.')

# SELECT State == 1
series_dict = {}
def select_series(db_conn):
    table_select = f"""
            SELECT Id, SeriesNumber, PseudoName, PseudoAcc
            FROM series WHERE State = 1;
        """
    try: 
        select_rows = db_conn.cursor().execute(table_select).fetchall()
        for row in select_rows:
            series_dict[row[0]] = row[3] + '_' + row[2] + '_' + str(row[1])
    except Error as err:
        print('\033[1;35mSELECT', err, '. \033[0m')

# SELECT State == 2
series_seg_array = []
def select_seg_series(db_conn):
    table_select = f"""
        SELECT PseudoAcc, PseudoName, SeriesNumber
        FROM series WHERE State=2
        ORDER BY PseudoAcc, SeriesNumber;
        """
    try: 
        select_rows = db_conn.cursor().execute(table_select).fetchall()
        for row in select_rows:
            series_seg_array.append(row[0] + '_' + row[1] + '_' + str(row[2]))
    except Error as err:
        print('\033[1;35mSELECT', err, '. \033[0m')

#UPDATE
def update_series(db_conn, seriesId) -> bool:
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
conn = sqlite3.connect(dbFile)
orthanc = Orthanc(orthancSrv, warn_insecure=False)

# INSERT State = 0/1
# insert_info_to_series()
# conn.commit()

# SELECT State == 1
# select_series(conn)
# for (key, value) in series_dict.items():
#     series_path = output_path + value
#     mkdirs(series_path)
#     print(series_path)
#     dcm_path = series_path + '/dcm/'
#     mkdirs(dcm_path)
#     nii_path = series_path + '/nifti/'
#     mkdirs(nii_path)
#     print("Get series instances ", end='')
#     os.system("find " + dcm_path + " -type l -delete")
#     insts = orthanc.get_series_instances(key)
#     for inst in insts:
#         fileUUID = inst['FileUuid']
#         raw_file = orthanc_path + fileUUID[0:2] + '/' + fileUUID[2:4] + '/' + fileUUID
#         os.system("ln -s " + raw_file + ' ' + dcm_path)
#         print('.', end='')
#     print("done!")
#     print("Waitng... dcm2niix ")
#     d2ncmd = d2n + value + para + nii_path + ' ' + dcm_path + ' > /dev/null'
#     os.system(d2ncmd)
#     print("done!")
#     seg_path = series_path + '/seg/'
#     mkdirs(seg_path)
#     nii_file = nii_path + value + '.nii.gz'
#     seg_file = seg_path + value + '_seg.nii.gz'
#     log_file = seg_path + value + '_log.txt'
#     print("Waitng... fetal_brain_seg ")
#     if os.path.isfile(nii_file):
#         segcmd = seg + nii_file + " --segment_output_names " + seg_file + " > " + log_file
#         os.system(segcmd)
#         print("done!")
#     else:
#         print('\033[1;35 ', nii_file, ' does not exists. \033[0m')
#     if os.path.isfile(seg_file) and update_series(conn, key):
#         conn.commit()
#         print(seg_file + " OK.")
#     else:
#         print('\033[1;35 Create ', nii_file, ' error. \033[0m')

# SELECT State == 2
# select_seg_series(conn)
# print(series_seg_array)
# for value in series_seg_array:
#     series_path = output_path + value
#     nii_path = series_path + '/nifti/'
#     nii_file = nii_path + value + '.nii.gz'
#     seg_path = series_path + '/seg/'
#     seg_file = seg_path + value + '_seg.nii.gz'
#     if os.path.isfile(nii_file) and os.path.isfile(seg_file):
#         print(seg_file)

conn.close()
