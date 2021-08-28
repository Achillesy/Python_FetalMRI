#!/usr/bin/env python
#
# Instructions:
# Batch process batch_prepare_dcms.py to prepare dicom files for mark.
#
# \author     Xuchu Liu (xuchu_liu@rush.edu)
# \date       08/24/2021
#

import os
import numpy as np
import pydicom
from PIL import Image

def normalization(data):
    _range = np.max(data) - np.min(data)
    return (data - np.min(data)) / _range

curDir = os.getcwd()
curFolder = os.walk(curDir)

dcmfile_list = list()
for path, dir_list, file_list in curFolder:
    for file_name in file_list:
        if '.dcm' in file_name:
            dcm_file = os.path.join(path, file_name)
            print(dcm_file)
            try:
                ds = pydicom.dcmread(dcm_file, force=True)
                new_jpg = Image.fromarray(normalization(ds.pixel_array)*255).convert('L')
                accession = ds.AccessionNumber
                series = '%02d' % (ds.SeriesNumber)
                instance = '%02d' % (ds.InstanceNumber)
                jpg_sag_name = '%s_%s_%s.jpg' % (accession, series, instance)
                new_jpg.save(jpg_sag_name, 'jpeg')
            except  Exception as e:
                print('Exception Reson:', e)
                pass
