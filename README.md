# Python_FetalMRI

https://github.com/gift-surg/NiftyMIC

https://github.com/gift-surg/MONAIfbs


  - Get docx from radiologist 得到用户相关资料
  - /FetalMRI/MONAIfbs/docx2csv patient.docx patient.csv 把docx转换为csv格式
  - /FetalMRI/MONAIfbs/writeOrigInfo2Backtracking.py patient.csv 把用户原始信息导入数据库
  - Get anonymize PACS and pseudo.xlsx 从PACS下载用户数据并获得匿名对照表
  - /FetalMRI/MONAIfbs/xlsx2csv pseudo.xlsx pseudo.csv (no need) 把xlsx转换为csv格式

```
├── manage_orthanc
│   └── writeCsv2Track.py
├── MONAIfbs
│   ├── batch_fetal_brain_dcm.py
│   ├── batch_fetal_brain_png.py
│   ├── batch_fetal_brain_seg.py
│   ├── batch_subject_space.py
│   ├── docx2csv.py                   把docx转换为csv格式
│   ├── fetaldb.py
│   ├── set_select_flag.py
│   ├── shownii.py
│   ├── tableBacktracking.py
│   ├── testPyDicom.py
│   ├── writeOrigInfo2Backtracking.py 把用户原始信息导入数据库
│   ├── writePseudo2Backtracking.py
│   └── xlsx2csv.py                   把xlsx转换为csv格式
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

## 数据结构
```sqlite
CREATE TABLE "backtracking" (
	"Id"	INTEGER,
	"OrigName"	TEXT,
	"OrigMR"	TEXT,
	"OrigAcc"	TEXT UNIQUE,
	"OrigGA"	TEXT,
	"PseudoAcc"	TEXT UNIQUE,
	"PseudoID"	TEXT UNIQUE,
	"PseudoName"	TEXT,
	"State"	INTEGER DEFAULT 0,
	PRIMARY KEY("Id" AUTOINCREMENT)
);

CREATE TABLE "series" (
	"Id"	TEXT,
	"PseudoID"	TEXT,
	"PseudoName"	TEXT,
	"PseudoAcc"	TEXT,
	"SeriesNumber"	INTEGER,
	"SeriesBrief"	TEXT,
	"SeriesDescription"	TEXT,
	"AcquisitionMatrix"	TEXT,
	"Rows"	INTEGER,
	"Columns"	INTEGER,
	"PixelSpacing"	TEXT,
	"Height"	INTEGER,
	"Width"	INTEGER,
	"SegCount"	INTEGER DEFAULT 0,
	"State"	INTEGER DEFAULT 0,
	PRIMARY KEY("Id")
);
```
