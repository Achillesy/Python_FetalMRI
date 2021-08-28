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
#   "PseudoAcc"	TEXT UNIQUE,
#   "PseudoID"	TEXT UNIQUE,
#   "PseudoName"	TEXT,
#   "State"	    INTEGER DEFAULT 0,
#   PRIMARY KEY("Id" AUTOINCREMENT)
# );
# Accession number lookup.csv (from xlsx)
# State:
#   0: insert original info
#   1: update pseduo info
#
# \author     Xuchu Liu (xuchu_liu@rush.edu)
# \date       03/06/2021
#

import os
import sys
sys.path.append('/mnt/Storage/Xuchu_Liu/Workspace/Python/FetalMRI')
import csv
from itertools import islice
from lib.fetaldb import FetalDB
# from openpyxl import load_workbook

if len(sys.argv) != 2:
    print("""
Write fseudo info to backtracking table. 

Usage: %s fseudo_info.csv
""" % (sys.argv[0]))
    exit(-1)

dbFile = "/mnt/Storage/Xuchu_Liu/Workspace/Python/FetalMRI/FetalMRIsqlite3.db"
info_file = sys.argv[1]

##########
conn = FetalDB(dbFile)

# UPDATE State = 1
#update_csv_to_backtracking(conn, csvAccFile)
cfile = open(info_file, 'r')
rows = csv.reader(cfile)
num = 0
succ = 0
for row in islice(rows, 0, None): #(iterable, start, stop[, step])
    num = num + 1
    PseudoAcc = row[0].zfill(6)
    if conn.update_backtracking(row[1], PseudoAcc, row[2]):
        print('UPDATE ' + row[2] + ' success.')
        succ = succ + 1
cfile.close()

print("Total %d of %d pseudo info update to backtracking table." % (succ, num))
conn.close()
