#!/usr/bin/env python
#
# Instructions:
# Get series info from Othanc and write to series table. 
# seriesId, SeriesDescription, SeriesDate, SeriesNumber, PixelBandwidth,
# PseudoID, PseudoName, PseudoAcc, State
#
# \date       03/10/2021
#
 
import re
import sqlite3
from sqlite3.dbapi2 import Error
from orthanc_rest_client import Orthanc

dbFile = "/mnt/Storage/Xuchu_Liu/orthanc/db-fetal/FetalMRIsqlite3.db"
orthancSrv = "http://localhost:8042"
orthanc_path = "/mnt/Storage/Xuchu_Liu/orthanc/db-v6/"

# Insert
def insert_series(db_conn, seriesId, PseudoID, PseudoName, PseudoAcc, \
        SeriesNumber, SeriesBrief, SeriesDescription, \
        AcquisitionMatrix, Rows, Columns, PixelSpacing, Height, Width, State) -> bool:
    table_insert = f"""
            INSERT INTO series (Id, PseudoID, PseudoName, PseudoAcc, \
            SeriesNumber, SeriesBrief, SeriesDescription, \
            AcquisitionMatrix, Rows, Columns, PixelSpacing, Height, Width, State)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """
    try:
        db_conn.cursor().execute(table_insert, (seriesId, \
            PseudoID, PseudoName, PseudoAcc, \
            SeriesNumber, SeriesBrief, SeriesDescription, \
            AcquisitionMatrix, Rows, Columns, PixelSpacing, Height, Width, State))
        return True
    except Error as err:
        print('\033[1;35mINSERT', seriesId, err, '. \033[0m')
        return False

##########
conn = sqlite3.connect(dbFile)
orthanc = Orthanc(orthancSrv, warn_insecure=False)

# INSERT State = 0/1
all_series = orthanc.get_series()
seriesNew = 0
for series in all_series:
    infoS = orthanc.get_series_shared_tags(series)
    infoI = orthanc.get_series_instances_tags(series)
    # PseudoID, PseudoName, PseudoAcc, \
    PseudoID = infoS['0010,0020']['Value']
    PseudoName = infoS['0010,0010']['Value']
    PseudoAcc = infoS['0008,0050']['Value']
    # SeriesNumber, SeriesBrief, SeriesDescription, State
    SeriesNumber = infoS['0020,0011']['Value']
    SeriesBrief = ''
    SeriesDescription = ''
    State = 0
    if '0008,103e' in infoS:
        SeriesDescription = infoS['0008,103e']['Value']
    elif '0008,103e' in infoI:
        SeriesDescription = infoI['0008,103e']['Value']
    SeriesDescriptionU = SeriesDescription.upper()
    if bool(re.search('(?=.*HASTE)(?=.*T2)(?=.*BRAIN)(?=.*(SAG|AX|COR))', \
            SeriesDescriptionU, re.IGNORECASE)):
        State = 1
        if SeriesDescriptionU.find("AX") > -1:
            SeriesBrief = "AX"
        if SeriesDescriptionU.find("SAG") > -1:
            SeriesBrief = "SAG"
        if SeriesDescriptionU.find("COR") > -1:
            SeriesBrief = "COR"
    # AcquisitionMatrix, Rows, Columns, PixelSpacing, Height, Width
    if '0018,1310' in infoS:
        AcquisitionMatrix = infoS['0018,1310']['Value']
    elif '0018,1310' in infoI:
        AcquisitionMatrix = infoI['0018,1310']['Value']
    if '0028,0010' in infoS:
        Rows = infoS['0028,0010']['Value']
    elif '0028,0010' in infoI:
        Rows = infoI['0028,0010']['Value']
    if '0028,0011' in infoS:
        Columns = infoS['0028,0011']['Value']
    if '0028,0011' in infoI:
        Columns = infoI['0028,0011']['Value']
    PixelSpacing = infoS['0028,0030']['Value']
    matrix = AcquisitionMatrix.split("\\")
    frequency = float(matrix[0])
    if frequency < float(matrix[1]):
        frequency = float(matrix[1])
    phase = float(matrix[2])
    if phase < float(matrix[3]):
        phase = float(matrix[3])
    spacing = PixelSpacing.split("\\")
    spacH = float(spacing[0])
    spacW = float(spacing[1])
    Height = round(spacH * frequency * 2)
    Width = round(spacW * phase * 2)
    if insert_series(conn, series, PseudoID, PseudoName, PseudoAcc, \
        SeriesNumber, SeriesBrief, SeriesDescription, \
        AcquisitionMatrix, Rows, Columns, PixelSpacing, Height, Width, State):
        print('INSERT ', PseudoName, PseudoAcc, SeriesNumber, ' success.')
        seriesNew += 1
print('Total of ' + str(seriesNew) + ' series INSERT success.')

conn.commit()   
conn.close()
