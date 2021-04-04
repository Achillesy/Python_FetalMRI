#!/usr/bin/env python
#
# Instructions:
# Write original info to backtracking table. 
# OrigName, OrigMR, OrigAcc, OrigGA, OrigImpression
#
# \author     Xuchu Liu (xuchu_liu@rush.edu)
# \date       03/10/2021
#

import sys
import csv
from itertools import islice
import fetaldb

if len(sys.argv) != 2:
    print("""
Write original info to backtracking table. 

Usage: %s original_info.csv
""" % (sys.argv[0]))
    exit(-1)

dbFile = "FetalMRIsqlite3.db"


##########
conn = fetaldb.FetalDB(dbFile)

# INSERT default State = 0
cfile = open(sys.argv[1], 'r')
rows = csv.reader(cfile)
num = 0
succ = 0
for row in islice(rows, 1, None):
    num = num + 1
    if conn.insert_backtracking(row[0], row[1], row[2], row[3]):
        print('INSERT ' + row[0] + ' success.')
        succ = succ + 1
cfile.close()

print("Total %d of %d original info insert to backtracking table." % (succ, num))
conn.close()
