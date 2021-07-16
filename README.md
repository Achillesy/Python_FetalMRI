# Python_FetalMRI

https://github.com/gift-surg/NiftyMIC

https://github.com/gift-surg/MONAIfbs


  - Get docx from radiologist
  - /FetalMRI/MONAIfbs/docx2csv patient.docx patient.csv
  - /FetalMRI/MONAIfbs/writeOrigInfo2Backtracking.py patient.csv
  - Get anonymize PACS and pseudo.xlsx
  - /FetalMRI/MONAIfbs/xlsx2csv pseudo.xlsx pseudo.csv (no need)

```
├── manage_orthanc
│   └── writeCsv2Track.py
├── MONAIfbs
│   ├── batch_fetal_brain_dcm.py
│   ├── batch_fetal_brain_png.py
│   ├── batch_fetal_brain_seg.py
│   ├── batch_subject_space.py
│   ├── docx2csv.py
│   ├── fetaldb.py
│   ├── set_select_flag.py
│   ├── shownii.py
│   ├── tableBacktracking.py
│   ├── testPyDicom.py
│   ├── writeOrigInfo2Backtracking.py
│   ├── writePseudo2Backtracking.py
│   └── xlsx2csv.py
├── NiftyMIC
│   └── batch_reconstruction.py 
├── batch_fetal_brain_seg.py
├── batch_reconstruction.py
├── batch_target_recon.py
├── dcm2nii.py
├── ImportDicomFiles.py
├── manage.py
├── tableSeries.py
└── writeOrthancInfo2Series.py
```