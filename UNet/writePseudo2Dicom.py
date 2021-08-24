#!/usr/bin/env python
#
# Instructions:
# Write Pseudo Name to dcm in Folder. 
# exam_PseudoAcc
#   |__seriesNumber_AX BrainT2 HASTE BH
#
# \author     Xuchu Liu (xuchu_liu@rush.edu)
# \date       08/17/2021
#

import sys
import os
import pydicom
import uuid

if len(sys.argv) != 3:
    print("""
Write Pseudo Name to dcm in Folder.

Usage: %s PseudoName PseudoAcc
""" % (sys.argv[0]))
    exit(-1)

PseudoName = sys.argv[1].rstrip('/')
PseudoAcc  = sys.argv[2].rstrip('/')

curDir = os.walk('./')
for path, dir_list, file_list in curDir:
    for file_name in file_list:
        if '.dcm' in file_name:
            dcm_file = os.path.join(path, file_name)
            ds = pydicom.dcmread(dcm_file)
            ds.PatientName = PseudoName
            ds.PatientID = str(uuid.uuid3(uuid.NAMESPACE_DNS, PseudoName))
            ds.AccessionNumber = PseudoAcc
            ds.save_as(dcm_file)
            print(dcm_file)
