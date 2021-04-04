#!/usr/bin/env python
#
# Instructions:
# Import patient info from docx file to csv. 
#
# \author     Xuchu Liu (xuchu_liu@rush.edu)
# \date       03/10/2021
#

from os import close, getgrouplist
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

def get_number(rawStr):
    strNum = ""
    numObj = re.search(r'\d+', rawStr)
    if numObj:
        strNum = numObj.group()
    return strNum
 
def get_name(rawStr):
    strName = re.sub(r'[^A-Za-z,]', "", rawStr)
    return strName

cfile = open(csvFile, 'w', newline='', encoding='utf-8-sig')
writer = csv.writer(cfile)
writer.writerow(["OrigName", "OrigMR", "OrigAcc", "OrigGA"])

rows = read_docx(docxFile)
OrigName = ""
OrigMR = ""
count = 0
for row in rows:
    if len(row) > 0:
        accObj = re.search(r'(.*?)\bAcc\b(.*)', row, re.IGNORECASE)
        if accObj:
            splitAcc = accObj.groups()
            mrObj = re.search(r'(.*?)\bMR\b(.*)', splitAcc[0], re.IGNORECASE)
            if mrObj:
                splitMR = mrObj.groups()
                rawName = splitMR[0]
                rawMR = splitMR[1]
            else: # Can't find #MR
                rawName = OrigName
                rawMR = OrigMR
            gaObj = re.search(r'(.*?)\bGA\b(.*)', splitAcc[1], re.IGNORECASE)
            if gaObj:
                splitGA = gaObj.groups()
                rawAcc = splitGA[0]
                rawGA = splitGA[1]
            else: # Can't find #GA
                rawAcc = splitAcc[1]
                rawGA = ""
            OrigAcc = get_number(rawAcc)
            OrigMR = get_number(rawMR)
            if len(OrigMR) < 4 and len(OrigAcc) < 4:
                print('\033[1;33;44m(no #MR)' + row + '\033[0m') # Debug
            else:
                OrigName = get_name(rawName)
                OrigGA = get_number(rawGA)
                count = count + 1
                print(count, [OrigName, OrigMR, OrigAcc, OrigGA]) # Debug
                writer.writerow([OrigName, OrigMR, OrigAcc, OrigGA])
        else: # Can't find #Acc
            print('\033[1;33;44m(no #Acc)' + row + '\033[0m') # Debug

cfile.close()
