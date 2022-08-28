#!/usr/bin/env python
#
# docker exec -it NiftyMIC /bin/bash
# cd /vboxshare/Data/FetalDataRush/20210819_asher_normal/exam_000105
# fetal_brain_seg.py
#
# Instructions:
# Traverse a patient(current) directory to generate Brain Segmentation.
#
# \author     Xuchu Liu (xuchu_liu@rush.edu)
# \date       08/16/2021
#
import os
import sys
from glob import glob

curDir = os.getcwd()
tarDir = curDir.replace('FetalDataRush', 'rush'+os.sep+'fetaldata').replace('Data', 'DataSet')
niftiDir = os.path.join(tarDir, 'nifti')
segDir = os.path.join(tarDir, 'seg')
srrDir = os.path.join(tarDir, 'srr')

d2n = 'dcm2niix -f %f_%s_%d -i y -x y -m y -v y -z y -o '
seg = "niftymic_segment_fetal_brains --filenames "
srr = "niftymic_run_reconstruction_pipeline --filenames "

if __name__=="__main__":

    # convert *.dicom to Foler_Serial_Descrip.nii.gz
    os.makedirs(niftiDir, exist_ok=True)
    d2ncmd = d2n + '"' + niftiDir + '" "' + curDir + '"'
    print(d2ncmd)
    os.system(d2ncmd)
    nii_ax_files = sorted(glob(niftiDir + os.sep +'*_[aA][xX]*.nii.gz'))
    nii_cor_files = sorted(glob(niftiDir + os.sep +'*_[cC][oO][rR]*.nii.gz'))
    nii_sag_files = sorted(glob(niftiDir + os.sep +'*_[sS][aA][gG]*.nii.gz'))
    nii_files = nii_ax_files+nii_cor_files+nii_sag_files
    special_chars = '() '
    for nii_file in nii_files:
        for s_char in special_chars:
            if s_char in nii_file:
                new_nii_file = nii_file.replace('(','').replace(')','').replace(' ', '_')
                os.rename(nii_file,new_nii_file)
                break

    nii_ax_files = sorted(glob(niftiDir + os.sep +'*_[aA][xX]*.nii.gz'))
    nii_cor_files = sorted(glob(niftiDir + os.sep +'*_[cC][oO][rR]*.nii.gz'))
    nii_sag_files = sorted(glob(niftiDir + os.sep +'*_[sS][aA][gG]*.nii.gz'))
    nii_files = nii_ax_files+nii_cor_files+nii_sag_files
    if len(nii_files)<1:
        sys.exit(1)
    os.makedirs(segDir, exist_ok=True)
    seg_files = [os.path.join(segDir, os.path.basename(nii_file).replace('.nii.gz', '_BrainSeg.nii.gz')) for nii_file in nii_files]
    segcmd = seg + ' '.join(nii_files) + ' --filenames-masks ' + ' '.join(seg_files)
    print(segcmd)
    os.system(segcmd)

    # seg_files = sorted(glob(segDir + os.sep +'*_BrainSeg.nii.gz'))
    # nii_files = [os.path.join(niftiDir, os.path.basename(seg_file).replace('_BrainSeg.nii.gz', '.nii.gz')) for seg_file in seg_files]
    # if len(nii_files)<1:
    #     sys.exit(1)
    # os.makedirs(srrDir, exist_ok=True)
    # srrcmd = srr + ' '.join(nii_files) + ' --filenames-masks ' + ' '.join(seg_files) + ' --dir-output ' + srrDir + ' --verbose 1'
    # print(srrcmd)
    # os.system(srrcmd)
