#!/usr/bin/env python
#
# Instructions:
# Write original info to backtracking table. 
# Fetal_MRI_Research_Cases_Normal_Brain.csv (from docx)
# OrigName, OrigMR, OrigAcc, OrigGA
#
# \author     Xuchu Liu (xuchu_liu@rush.edu)
# \date       03/10/2021
#

import sys
sys.path.append('/mnt/Storage/Xuchu_Liu/Workspace/Python/FetalMRI')
import csv
from itertools import islice
from dblib.fetaldb import FetalDB

if len(sys.argv) != 2:
    print("""
Write original info to backtracking table. 

Usage: %s original_info.csv
""" % (sys.argv[0]))
    exit(-1)

dbFile = "/mnt/Storage/Xuchu_Liu/Workspace/Python/FetalMRI/FetalMRIsqlite3.db"
info_file = sys.argv[1]

##########
conn = FetalDB(dbFile)

# INSERT default State = 0
cfile = open(info_file, 'r')
rows = csv.reader(cfile)
num = 0
succ = 0
for row in islice(rows, 1, None): #(iterable, start, stop[, step])
    num = num + 1
    if conn.insert_backtracking(row[0], row[1], row[2], row[3]):
        print('INSERT ' + row[0] + ' success.')
        succ = succ + 1
cfile.close()

print("Total %d of %d original info insert to backtracking table." % (succ, num))
conn.close()
