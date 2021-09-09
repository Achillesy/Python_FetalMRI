#!/usr/bin/env python
#
# Instructions:
# Write Pons json info to instance table.
#
# SAG Pons          A.P Diameter of Pons
# SAG Vermis        A.P Diameter of Vermis
# SAG HVermis       Height of vermis
# SAG Cisterna      Cisterna Magna
# SAG Fronto        Fronto-Occipital Diameter
# AX  AtrialR       Atrial Diameter of Lat Ventricle R
# AX  AtrialL       Atrial Diameter of Lat Ventricle L
# COR  Cerebellar    Transverse Cerebellar
# COR Biparietal    Cerebral Biparietal Diameter
#
# Pons_1x,       Pons_1y
# Pons_2x,       Pons_2y
# Vermis_1x,     Vermis_1y
# Vermis_2x,     Vermis_2y
# HVermis_1x,    HVermis_1y
# HVermis_2x,    HVermis_2y
# Cisterna_1x,   Cisterna_1y
# Cisterna_2x,   Cisterna_2y
# Fronto_1x,     Fronto_1y
# Fronto_2x,     Fronto_2y
# AtrialR_1x,    AtrialR_1y
# AtrialR_2x,    AtrialR_2y
# AtrialL_1x,    AtrialL_1y
# AtrialL_2x,    AtrialL_2y
# Cerebellar_1x, Cerebellar_1y
# Cerebellar_2x, Cerebellar_2y
# Biparietal_1x, Biparietal_1y
# Biparietal_2x, Biparietal_2y
#
# \author     Xuchu Liu (xuchu_liu@rush.edu)
# \date       09/02/2021
#

import os
import sys
sys.path.append('/mnt/Storage/Xuchu_Liu/Workspace/Python/FetalMRI')
import json
import uuid

from dblib.fetaldb import FetalDB

dbFile = "/mnt/Storage/Xuchu_Liu/Workspace/Python/FetalMRI/FetalMRIsqlite3.db"
json_path_1 = "/home/achilles/Workspace/DataSet/FetalData/20210716_Jubril_GUI"
json_path_2 = "/home/achilles/Workspace/DataSet/FetalData/20210830_Jubril_GUI"
json_path_3 = "/home/achilles/Workspace/Data/fetal/json"
json_path_4 = "/home/achilles/Workspace/DataSet/FetalData/20210906_Jubril_GUI"
json_path_5 = "/home/achilles/Workspace/DataSet/FetalData/20210907_Jubril_GUI"

curFolder = os.walk(json_path_5)

# ##########
conn = FetalDB(dbFile)

num = 0
succ = 0

for path, dir_list, file_list in curFolder:
    for file_name in file_list:
        # A.P Diameter of Vermis
        if '_Diameter_of_Vermis.json' in file_name:
            json_file = os.path.join(path, file_name)
            print(json_file)
            num = num + 1
            try:
                with open(json_file, 'r') as f:
                    seg_info = json.load(f)
                accession = seg_info['Measurement']['AccessionNumber']
                series = seg_info['Measurement']['SeriesNumber']
                if len(series) < 2:
                    series = '0' + series
                instance = seg_info['Measurement']['InstanceNumber']
                if len(instance) < 2:
                    instance = '0' + instance
                seriesName = accession + '_' + series
                instanceName = accession + '_' + series + '_' + instance
                key = str(uuid.uuid3(uuid.NAMESPACE_DNS, instanceName))
                Vermis_1x, Vermis_1y = seg_info['Measurement']['mask1']
                Vermis_2x, Vermis_2y = seg_info['Measurement']['mask2']
                # print(key, Vermis_1x, Vermis_1y, Vermis_2x, Vermis_2y)
                if conn.update_instance_vermis(key, Vermis_1x-1, Vermis_1y-1, Vermis_2x-1, Vermis_2y-1):
                    print('UPDATE ' + key + ' success.')
                    succ = succ + 1
            except  Exception as e:
                print('Exception Reason:', e)
                pass

print("Total %d of %d segmentation info update to instance table." % (succ, num))
conn.close()
