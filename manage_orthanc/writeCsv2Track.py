#!/usr/bin/env python
#
# Instructions:
# Write original info from csv file to track table. 
# OrigName, OrigMR, OrigAcc, OrigGA
#
# \author     Xuchu Liu (xuchu_liu@rush.edu)
# \date       03/10/2021
#

import sys
import sqlite3
from sqlite3.dbapi2 import Error
import csv

if len(sys.argv) != 2:
    print("""
Write original info to backtracking table. 

Usage: %s original_info.csv
""" % (sys.argv[0]))
    exit(-1)

dbFile = "/mnt/Storage/Xuchu_Liu/orthanc/db-fetal/FetalMRIsqlite3.db"

# Insert
def insert_backtracking(db_conn, OrigName, OrigMR, OrigAcc, OrigGA, OrigImpression) -> bool:
    table_insert = f"""
            INSERT INTO backtracking(OrigName, OrigMR, OrigAcc, OrigGA, OrigImpression)
            VALUES (?, ?, ?, ?, ?);
        """
    try:
        db_conn.cursor().execute(table_insert, \
            (OrigName, OrigMR, OrigAcc, OrigGA, OrigImpression))
        return True
    except Error as err:
        print('\033[1;35mINSERT ', OrigName, OrigMR, OrigAcc, err, '. \033[0m')
        return False

##########
conn = sqlite3.connect(dbFile)

# INSERT default State = 0
cfile = open(sys.argv[1], 'r')
rows = csv.reader(cfile)
num = 0
succ = 0
for row in rows:
    num = num + 1
    if insert_backtracking(conn, row[0], row[1], row[2], row[3], row[4]):
        print('INSERT ' + row[0] + ' success.')
        succ = succ + 1
cfile.close()

if succ > 0:
    conn.commit()

print("Total %d of %d original info insert to backtracking table." % (succ, num))
conn.close()
