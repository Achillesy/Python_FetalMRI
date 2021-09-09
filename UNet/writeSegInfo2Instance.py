#!/usr/bin/env python
#
# Instructions:
# Write _seg_info.json info to instance table.
#
#
# \author     Xuchu Liu (xuchu_liu@rush.edu)
# \date       08/28/2021
#

import os
import sys
sys.path.append('/mnt/Storage/Xuchu_Liu/Workspace/Python/FetalMRI')
import json

from dblib.fetaldb import FetalDB

dbFile = "/mnt/Storage/Xuchu_Liu/Workspace/Python/FetalMRI/FetalMRIsqlite3.db"
dcm_path_1 = "/home/achilles/Workspace/DataSet/FetalData/20210301_asher"
dcm_path_2 = "/home/achilles/Workspace/DataSet/FetalData/20210819_asher"
dcm_path_t = "/home/achilles/Workspace/DataSet/FetalData/20210824_test"

curFolder = os.walk(dcm_path_1)

# ##########
conn = FetalDB(dbFile)

num = 0
succ = 0
for path, dir_list, file_list in curFolder:
    for file_name in file_list:
        if '_seg_info.json' in file_name:
            json_file = os.path.join(path, file_name)
            print(json_file)
            try:
                with open(json_file, 'r') as f:
                    seg_info = json.load(f)
                for key in seg_info:
                    num = num + 1
                    if conn.update_instance(key, seg_info[key]['SegX'], seg_info[key]['SegWidth'], seg_info[key]['SegY'], seg_info[key]['SegHeight']):
                        print('UPDATE ' + key + ' success.')
                        succ = succ + 1
            except  Exception as e:
                print('Exception Reason:', e)
                pass

print("Total %d of %d segmentation info update to instance table." % (succ, num))
conn.close()
