#!/usr/bin/env python
#
# Instructions:
# Batch process batch_A_P_Diameter_of_Pons.py to mark Pons.
#
# \author     Xuchu Liu (xuchu_liu@rush.edu)
# \date       08/16/2021
#

import os



series_list = list()
for path, dir_list, file_list in curDir:
    for file_name in file_list:
        if '.dcm' in file_name:
            series_list.append(path)
            break