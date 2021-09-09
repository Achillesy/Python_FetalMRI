#!/usr/bin/env python
#
# Instructions:
# Write dicom files info to instance table.
#
# CREATE TABLE "instance" (
# 	"Id"	TEXT,
# 	"DicomPath"	TEXT NOT NULL,
# 	"PseudoAcc"	TEXT NOT NULL,
# 	"SeriesNumber"	INTEGER NOT NULL,
# 	"InstanceNumber"	INTEGER NOT NULL,
#	 "SliceLocation"	REAL DEFAULT 0,
# 	"SeriesBrief"	TEXT,
# 	"Rows"	TEXT DEFAULT 512,
# 	"Columns"	INTEGER DEFAULT 512,
# 	"PixelSpacing1"	REAL NOT NULL,
# 	"PixelSpacing2"	REAL NOT NULL,
# 	"SegX"	INTEGER DEFAULT 0,
# 	"SegWidth"	INTEGER DEFAULT 512,
# 	"SegY"	INTEGER DEFAULT 0,
# 	"SegHeight"	INTEGER DEFAULT 0,
# 	"State"	INTEGER DEFAULT 0,
# 	PRIMARY KEY("Id")
# );
#
# \author     Xuchu Liu (xuchu_liu@rush.edu)
# \date       08/25/2021
#

import os
import sys
sys.path.append('/mnt/Storage/Xuchu_Liu/Workspace/Python/FetalMRI')
import pydicom
import uuid

from dblib.fetaldb import FetalDB

dbFile = "/mnt/Storage/Xuchu_Liu/Workspace/Python/FetalMRI/FetalMRIsqlite3.db"
dcm_path_1 = "/home/achilles/Workspace/DataSet/FetalData/20210301_asher"
dcm_path_2 = "/home/achilles/Workspace/DataSet/FetalData/20210819_asher"
dcm_path_t = "/home/achilles/Workspace/DataSet/FetalData/20210824_test"

curFolder = os.walk(dcm_path_2)

# ##########
conn = FetalDB(dbFile)

num = 0
succ = 0
for path, dir_list, file_list in curFolder:
    for file_name in file_list:
        if '.dcm' in file_name:
            dcm_file = os.path.join(path, file_name)
            print(dcm_file)
            num = num + 1
            try:
                ds = pydicom.dcmread(dcm_file, force=True)
                # INSERT instance default State = 0
                accession = ds.AccessionNumber
                series = '%02d' % (ds.SeriesNumber)
                instance = '%02d' % (ds.InstanceNumber)
                instanceName = accession + '_' + series + '_' + instance
                instanceId = str(uuid.uuid3(uuid.NAMESPACE_DNS, instanceName))
                seriesDescU = ds.SeriesDescription.upper()
                seriesBrief=''
                if 'AX' in seriesDescU:
                    seriesBrief = 'AX'
                if 'SAG' in seriesDescU:
                    seriesBrief = 'SAG'
                if 'COR' in seriesDescU:
                    seriesBrief = 'COR'
                rows = ds.Rows
                columns = ds.Columns
                pixelSpacing1, pixelSpacing2 = ds.PixelSpacing
                if conn.insert_instance(instanceId, dcm_file, accession, series, instance, seriesBrief, rows, columns, pixelSpacing1, pixelSpacing2):
                    print('INSERT ' + accession + ' success.')
                    succ = succ + 1
            except  Exception as e:
                print('Exception Reason:', e)
                pass

print("Total %d of %d dicom info insert to instance table." % (succ, num))
conn.close()
