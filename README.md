# Python_FetalMRI

https://github.com/gift-surg/NiftyMIC

https://github.com/gift-surg/MONAIfbs

## 开发步骤
  - Get docx from radiologist 得到用户相关资料
  - /FetalMRI/MONAIfbs/docx2csv patient.docx patient.csv 把docx转换为csv格式
  - /FetalMRI/MONAIfbs/writeOrigInfo2Backtracking.py patient.csv 把用户原始信息导入数据库
  - Get anonymize PACS and pseudo.xlsx 从PACS下载用户数据并获得匿名对照表
  - /FetalMRI/MONAIfbs/xlsx2csv pseudo.xlsx pseudo.csv (no need) 把xlsx转换为csv格式

## 文件列表
```
├── lib
│   ├── __init__.py
│   └── fetaldb.py                    操作数据库lib
├── manage_orthanc
│   └── writeCsv2Track.py             老版writeOrigInfo2Backtracking.py
├── MONAIfbs
│   ├── batch_fetal_brain_dcm.py      把婴儿脑部从全图中割离出来（包括黑边）
│   ├── batch_fetal_brain_png.py      把当前子目录下的seg转换为png背景图
│   ├── batch_fetal_brain_seg.py      使用dcm2niix把序列转换为nii.gz，然后执行fetal_brain_seg分割
│   ├── batch_subject_space.py        批量生成3D模型（不做位置矫正）
│   ├── docx2csv.py                   把docx转换为csv格式
│   ├── set_select_flag.py            手动修改数据库中的serias状态
│   ├── shownii.py                    显示nii.gz文件
│   ├── tableBacktracking.py          旧版批量修改dcm的PatientName, PatientID
│   ├── testPyDicom.py                测试pydicom库
│   ├── writeOrigInfo2Backtracking.py 把用户原始信息导入数据库
│   ├── writePseudo2Backtracking.py   批量修改dcm的PatientName, PatientID
│   └── xlsx2csv.py                   把xlsx转换为csv格式
├── NiftyMIC
│   └── batch_reconstruction.py       批量生成3D模型
├── UNet
│   ├── batch_dcm2jpg.py              把目录下的dcm转jpg
│   ├── batch_folder_seg.py           遍历目录生成_seg.nii.gz文件
│   ├── batch_prepare_dcms.py         筛选适合标注的dcm文件
│   ├── get_seg_info.py               从XXX_seg.nii.gz中提取seg信息到XXX_seg_info.json
│   ├── writeDicom2Instance.py        把dicom信息写入instance
│   ├── writePseudo2Dicom.py          将虚拟的用户名和AccNumber写入目录下的dcm文件
│   └── writeSegInfo2Instance.py      将segment信息写入instance
├── batch_fetal_brain_seg.py          旧版使用dcm2niix把序列转换为nii.gz，然后执行fetal_brain_seg分割
├── batch_reconstruction.py           老版批量生成3D模型
├── batch_target_recon.py             旧版批量生成3D模型
├── dcm2nii.py                        dcm转换为nii.gz
├── ImportDicomFiles.py               dicom导入orthanc
├── tableSeries.py                    老版使用dcm2niix把序列转换为nii.gz，然后执行fetal_brain_seg分割
└── writeOrthancInfo2Series.py        把Orthanc中的相关信息写入sqlite数据库
```

## 数据结构
```sql
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

CREATE TABLE "instance" (
	"Id"	TEXT,
	"DicomPath"	TEXT NOT NULL,
	"PseudoAcc"	TEXT NOT NULL,
	"SeriesNumber"	INTEGER NOT NULL,
	"InstanceNumber"	INTEGER NOT NULL,
	"SliceLocation"	REAL DEFAULT 0,
	"SeriesBrief"	TEXT,
	"Rows"	TEXT DEFAULT 512,
	"Columns"	INTEGER DEFAULT 512,
	"PixelSpacing1"	REAL NOT NULL,
	"PixelSpacing2"	REAL NOT NULL,
	"SegX"	INTEGER DEFAULT 0,
	"SegWidth"	INTEGER DEFAULT 0,
	"SegY"	INTEGER DEFAULT 0,
	"SegHeight"	INTEGER DEFAULT 0,
	"State"	INTEGER DEFAULT 0,
	PRIMARY KEY("Id")
);
```
## series的标志位
```
# table series State
#     0: import from orthanc
#     1: SeriesDescription AX/COR/SAG
#     2: fatal_brain_seg OK
#     3: selected to reconstruction
#     4: reconstructoion OK
#     5: no template dir
#     6: no subject dir
#     9: target stack
```
