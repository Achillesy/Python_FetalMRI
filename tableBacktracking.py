#!/usr/bin/env python

#
# Instructions:
# 1. Sqlite3 DB: FetalMRIsqlite3.db
# 2. Table:      backtracking
# CREATE TABLE "backtracking" (
#   "Id"	    INTEGER,
#   "OrigName"	TEXT,
#   "OrigMR"	TEXT UNIQUE,
#   "OrigAcc"	TEXT UNIQUE,
#   "OrigGA"	TEXT,
#   "OrigImpression"	TEXT,
#   "PseudoAcc"	TEXT UNIQUE,
#   "PseudoID"	TEXT UNIQUE,
#   "PseudoName"	TEXT,
#   "State"	    INTEGER DEFAULT 0,
#   PRIMARY KEY("Id" AUTOINCREMENT)
# );
#
# State:
#   0: insert original info
#   1: update pseduo info
#
# \author     Xuchu Liu (xuchu_liu@rush.edu)
# \date       03/06/2021
#

import os
import sys
import os.path
import sqlite3
from sqlite3.dbapi2 import Error
import csv
import pydicom
import SimpleITK as sitk

csvOrigFile = '../FetalData/20210301/Fetal_MRI_Research_Cases_Normal_Brain.csv'
csvAccFile = '../FetalData/20210301/Accession number lookup.csv'
dicomPath = '../FetalData/20210301'

dbFile = "FetalMRIsqlite3.db"

#UPDATE
def update_backtracking(db_conn, PseudoAcc, PseudoName, PseudoID, OrigAcc) -> bool:
    table_update = f"""
            UPDATE backtracking
            SET PseudoAcc = ?,
            PseudoName = ?,
            PseudoID = ?,
            State = 1
            WHERE OrigAcc = ?;
        """
    try:
        db_conn.cursor().execute(table_update, \
            (PseudoAcc, PseudoName, PseudoID, OrigAcc))
        return True
    except Error as err:
        print('\033[1;35mUPDATE ', PseudoAcc, PseudoName, OrigAcc, err, '. \033[0m')
        return False

def update_csv_to_backtracking(db_conn, filename):
    cfile = open(filename, 'r')
    rows = csv.reader(cfile)
    for row in rows:
        PseudoAcc = row[0].zfill(6)
        if update_backtracking(db_conn, PseudoAcc, row[2], row[3], row[1]):
            print('UPDATE ' + row[2] + ' success.')
    cfile.close()

# SELECT
acc_dict = {}
def select_backtracking(db_conn):
    table_select = f"""
            SELECT PseudoAcc, PseudoName, PseudoID
            FROM backtracking WHERE State > 0;
        """
    try: 
        select_rows = db_conn.cursor().execute(table_select).fetchall()
        for row in select_rows:
            acc_dict[row[0]] = [row[1], row[2]]
    except Error as err:
        print('\033[1;35mSELECT ', err, '. \033[0m')

def modify_DicomTag(filename):
    if filename.endswith(".dcm"):
        ds = pydicom.dcmread(filename)
        pseduoAcc = ds.AccessionNumber
        ds.PatientName = acc_dict[pseduoAcc][0]
        ds.PatientID = acc_dict[pseduoAcc][1]
        print(pseduoAcc, ds.PatientName, ds.PatientID)
        ds.save_as(filename)

##########
conn = sqlite3.connect(dbFile)

# UPDATE State = 1
#update_csv_to_backtracking(conn, csvAccFile)
#conn.commit()

# SELECT State > 0
select_backtracking(conn)
if os.path.isfile(dicomPath):
    modify_DicomTag(dicomPath)
else:
    # Recursively modify a directory
    for root, dirs, files in os.walk(dicomPath):
        for f in files:
            modify_DicomTag(os.path.join(root, f))

conn.close()
