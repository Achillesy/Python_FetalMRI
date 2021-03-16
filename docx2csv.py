#!/usr/bin/env python
#
# Instructions:
# Import patient info from docx file to csv. 
#
# \author     Xuchu Liu (xuchu_liu@rush.edu)
# \date       03/10/2021
#

from os import close
import sys
import docx2txt
import re
import csv

if len(sys.argv) != 3:
    print("""
Import patient info from docx file to csv. 

Usage: %s patient.docx paitent.csv
""" % (sys.argv[0]))
    exit(-1)

docxFile = sys.argv[1]
csvFile = sys.argv[2]

def read_docx(filename):
    txt = docx2txt.process(filename)
    rows = txt.splitlines()
    return rows
 
cfile = open(csvFile, 'w', newline='', encoding='utf-8-sig')
writer = csv.writer(cfile)
rows = read_docx(docxFile)
for row in rows:
    if len(row) > 0:
        splitMR = row.split("MR#", 1)
        OrigName = ""
        OrigMR = ""
        OrigAcc = ""
        OrigGA = ""
        OrigImpression = ""
        if len(splitMR) > 1:
            OrigName = splitMR[0]
            p = re.compile("[0-9|.|,]")
            OrigName = p.sub('', splitMR[0]).strip()
            splitAcc = splitMR[1].split("Acc", 1)
            OrigMR = ''.join([c for c in str(splitAcc[0]) if c in '1234567890'])
            if len(splitAcc) > 1:
                splitGA = splitAcc[1].split("GA", 1)
                OrigAcc = ''.join([c for c in str(splitGA[0]) if c in '1234567890'])
                if len(splitGA) > 1:
                    splitImpression = re.split("[w|W|?]", splitGA[1], 1)
                    p = re.compile("[=|\s]")
                    OrigGA = p.sub('', splitImpression[0])
                    if len(splitImpression) > 1:
                        OrigImpression = splitImpression[1].split(' ', 1)[1]
            print([OrigName, OrigMR, OrigAcc, OrigGA, OrigImpression]) # Debug
            writer.writerow([OrigName, OrigMR, OrigAcc, OrigGA, OrigImpression])
        else:
            print('\033[1;33;44m' + row + '\033[0m') # Debug

cfile.close()
