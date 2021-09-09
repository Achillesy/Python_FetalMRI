import sqlite3

class FetalDB:
    ## The constructor of the FetalDB
    def __init__(self, name=None):
        self.conn = None
        self.cursor = None
        if name:
            self.open(name)
    
    ## Opens a new FetalDB connection.
    def open(self, name):
        try:
            self.conn = sqlite3.connect(name)
            self.cursor = self.conn.cursor()
        except sqlite3.Error as e:
            print("\033[1;35mError connecting to FetalDB\033[0m")

    ## Close a FetalDB connection.
    def close(self):
        if self.conn:
            self.conn.commit()
            self.cursor.close()
            self.conn.close()
    
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    ## SELECT Series State == 1 GROUP BY PseudoAcc
    def select_series_pseudoid(self, state):
        pseudoid_dict = {}
        table_select = f"""
                SELECT PseudoID, PseudoName, PseudoAcc
                FROM series WHERE State = ?
                GROUP BY PseudoAcc;
            """
        try:
            select_rows = self.cursor.execute(table_select, (state)).fetchall()
            for row in select_rows:
                pseudoid_dict[row[0]] = row[2] + '_' + str(row[1])
        except sqlite3.Error as err:
            print('\033[1;35mSELECT', err, '. \033[0m')
        return pseudoid_dict

    ## SELECT Series FOREACH PseudoID
    def select_series_id(self, PseudoId, state):
        seriesnumber_dict = {}
        table_select = f"""
                SELECT Id, SeriesNumber, SeriesBrief, Height, Width
                FROM series WHERE State = ?
                AND PseudoID = ?;
            """
        try:
            select_rows = self.cursor.execute(table_select, (state, PseudoId)).fetchall()
            for row in select_rows:
                seriesnumber_dict[row[0]] = str(row[1]) + '_' + row[2] + '_' + str(row[3]) + 'x' + str(row[4])
        except sqlite3.Error as err:
            print('\033[1;35mSELECT', PseudoId, err, '. \033[0m')
        return seriesnumber_dict

    ## UPDATE Series State
    def update_series_state(self, seriesId, state) -> bool:
        table_update = f"""
                UPDATE series
                SET State = ?
                WHERE Id = ?;
            """
        try:
            self.cursor.execute(table_update, (state, seriesId))
            return True
        except sqlite3.Error as err:
            print('\033[1;35mUPDATE State of ', seriesId, err, '. \033[0m')
            return False

    ## UPDATE Series SegCount
    def update_series_segcount(self, seriesId, segcount) -> bool:
        table_update = f"""
                UPDATE series
                SET SegCount = ?
                WHERE Id = ?;
            """
        try:
            self.cursor.execute(table_update, (segcount, seriesId))
            return True
        except sqlite3.Error as err:
            print('\033[1;35mUPDATE State of ', seriesId, err, '. \033[0m')
            return False

    ## UPDATE Series State by Reconstruction Result
    def update_series_state_recon(self, pseudoAcc, seriesNum, state) -> bool:
        table_update = f"""
                UPDATE series
                SET State = ?
                WHERE PseudoAcc = ? AND SeriesNumber = ?;
            """
        try:
            self.cursor.execute(table_update, (state, pseudoAcc, seriesNum))
            return True
        except sqlite3.Error as err:
            print('\033[1;35mUPDATE ', pseudoAcc, seriesNum, err, '. \033[0m')
            return False

    ## INSERT Origal Infomation from CSV
    def insert_backtracking(self, OrigName, OrigMR, OrigAcc, OrigGA) -> bool:
        table_insert = f"""
                INSERT INTO backtracking(OrigName, OrigMR, OrigAcc, OrigGA)
                VALUES (?, ?, ?, ?);
            """
        try:
            self.cursor.execute(table_insert, (OrigName, OrigMR, OrigAcc, OrigGA))
            return True
        except sqlite3.Error as err:
            print('\033[1;35mINSERT ', OrigName, OrigMR, OrigAcc, err, '. \033[0m')
            return False

    ## UPDATE Pseudo Information from CSV
    def update_backtracking(self, OrigAcc, PseudoAcc, PseudoName) -> bool:
        table_update = f"""
                UPDATE backtracking
                SET PseudoAcc = ?,
                PseudoName = ?,
                State = 1
                WHERE OrigAcc = ?;
            """
        try:
            self.cursor.execute(table_update, (PseudoAcc, PseudoName, OrigAcc))
            return True
        except sqlite3.Error as err:
            print('\033[1;35mUPDATE ', PseudoAcc, PseudoName, OrigAcc, err, '. \033[0m')
            return False

    ## INSERT Instance Infomation from Dicom Files
    def insert_instance(self, InstanceId, DicomPath, PseudoAcc, SeriesNumber, InstanceNumber, SeriesBrief, Rows, Columns, PixelSpacing1, PixelSpacing2) -> bool:
        table_insert = f"""
                INSERT INTO instance(Id, DicomPath, PseudoAcc, SeriesNumber, InstanceNumber, SeriesBrief, Rows, Columns, PixelSpacing1, PixelSpacing2)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """
        try:
            self.cursor.execute(table_insert, (InstanceId, DicomPath, PseudoAcc, SeriesNumber, InstanceNumber, SeriesBrief, Rows, Columns, PixelSpacing1, PixelSpacing2))
            return True
        except sqlite3.Error as err:
            print('\033[1;35mINSERT ', PseudoAcc, SeriesNumber, InstanceNumber, err, '. \033[0m')
            return False

    ## UPDATE Segmentation Information from _seg_info.json
    def update_instance(self, InstanceId, SegX, SegWidth, SegY, SegHeight) -> bool:
        table_update = f"""
                UPDATE instance
                SET SegX = ?,
                SegWidth = ?,
                SegY = ?,
                SegHeight = ?,
                State = 1
                WHERE Id = ?;
            """
        try:
            self.cursor.execute(table_update, (SegX, SegWidth, SegY, SegHeight, InstanceId))
            return True
        except sqlite3.Error as err:
            print('\033[1;35mUPDATE ', InstanceId, err, '. \033[0m')
            return False

    ## UPDATE Pons Information from _seg_info.json
    def update_instance_pons(self, InstanceId, Pons_1x, Pons_1y, Pons_2x, Pons_2y) -> bool:
        table_update = f"""
                UPDATE instance
                SET Pons_1x = ?,
                Pons_1y = ?,
                Pons_2x = ?,
                Pons_2y = ?,
                State = 2
                WHERE Id = ?;
            """
        try:
            self.cursor.execute(table_update, (Pons_1x, Pons_1y, Pons_2x, Pons_2y, InstanceId))
            return True
        except sqlite3.Error as err:
            print('\033[1;35mUPDATE Pons ', InstanceId, err, '. \033[0m')
            return False

    ## UPDATE Vermis Information from _seg_info.json
    def update_instance_vermis(self, InstanceId, Vermis_1x, Vermis_1y, Vermis_2x, Vermis_2y) -> bool:
        table_update = f"""
                UPDATE instance
                SET Vermis_1x = ?,
                Vermis_1y = ?,
                Vermis_2x = ?,
                Vermis_2y = ?,
                State = 2
                WHERE Id = ?;
            """
        try:
            self.cursor.execute(table_update, (Vermis_1x, Vermis_1y, Vermis_2x, Vermis_2y, InstanceId))
            return True
        except sqlite3.Error as err:
            print('\033[1;35mUPDATE Vermis ', InstanceId, err, '. \033[0m')
            return False

    ## UPDATE Height of Vermis Information from _seg_info.json
    def update_instance_hvermis(self, InstanceId, HVermis_1x, HVermis_1y, HVermis_2x, HVermis_2y) -> bool:
        table_update = f"""
                UPDATE instance
                SET HVermis_1x = ?,
                HVermis_1y = ?,
                HVermis_2x = ?,
                HVermis_2y = ?,
                State = 2
                WHERE Id = ?;
            """
        try:
            self.cursor.execute(table_update, (HVermis_1x, HVermis_1y, HVermis_2x, HVermis_2y, InstanceId))
            return True
        except sqlite3.Error as err:
            print('\033[1;35mUPDATE Height of Vermis ', InstanceId, err, '. \033[0m')
            return False

    ## UPDATE Cisterna Information from _seg_info.json
    def update_instance_cisterna(self, InstanceId, Cisterna_1x, Cisterna_1y, Cisterna_2x, Cisterna_2y) -> bool:
        table_update = f"""
                UPDATE instance
                SET Cisterna_1x = ?,
                Cisterna_1y = ?,
                Cisterna_2x = ?,
                Cisterna_2y = ?,
                State = 2
                WHERE Id = ?;
            """
        try:
            self.cursor.execute(table_update, (Cisterna_1x, Cisterna_1y, Cisterna_2x, Cisterna_2y, InstanceId))
            return True
        except sqlite3.Error as err:
            print('\033[1;35mUPDATE Cisterna ', InstanceId, err, '. \033[0m')
            return False

    ## UPDATE Fronto Information from _seg_info.json
    def update_instance_fronto(self, InstanceId, Fronto_1x, Fronto_1y, Fronto_2x, Fronto_2y) -> bool:
        table_update = f"""
                UPDATE instance
                SET Fronto_1x = ?,
                Fronto_1y = ?,
                Fronto_2x = ?,
                Fronto_2y = ?,
                State = 2
                WHERE Id = ?;
            """
        try:
            self.cursor.execute(table_update, (Fronto_1x, Fronto_1y, Fronto_2x, Fronto_2y, InstanceId))
            return True
        except sqlite3.Error as err:
            print('\033[1;35mUPDATE Fronto ', InstanceId, err, '. \033[0m')
            return False

    ## UPDATE AtrialR Information from _seg_info.json
    def update_instance_atrialr(self, InstanceId, AtrialR_1x, AtrialR_1y, AtrialR_2x, AtrialR_2y) -> bool:
        table_update = f"""
                UPDATE instance
                SET AtrialR_1x = ?,
                AtrialR_1y = ?,
                AtrialR_2x = ?,
                AtrialR_2y = ?,
                State = 3
                WHERE Id = ?;
            """
        try:
            self.cursor.execute(table_update, (AtrialR_1x, AtrialR_1y, AtrialR_2x, AtrialR_2y, InstanceId))
            return True
        except sqlite3.Error as err:
            print('\033[1;35mUPDATE AtrialR ', InstanceId, err, '. \033[0m')
            return False

    ## UPDATE AtrialL Information from _seg_info.json
    def update_instance_atriall(self, InstanceId, AtrialL_1x, AtrialL_1y, AtrialL_2x, AtrialL_2y) -> bool:
        table_update = f"""
                UPDATE instance
                SET AtrialL_1x = ?,
                AtrialL_1y = ?,
                AtrialL_2x = ?,
                AtrialL_2y = ?,
                State = 3
                WHERE Id = ?;
            """
        try:
            self.cursor.execute(table_update, (AtrialL_1x, AtrialL_1y, AtrialL_2x, AtrialL_2y, InstanceId))
            return True
        except sqlite3.Error as err:
            print('\033[1;35mUPDATE AtrialL ', InstanceId, err, '. \033[0m')
            return False

    ## UPDATE Cerebellar Information from _seg_info.json
    def update_instance_cerebellar(self, InstanceId, Cerebellar_1x, Cerebellar_1y, Cerebellar_2x, Cerebellar_2y) -> bool:
        table_update = f"""
                UPDATE instance
                SET Cerebellar_1x = ?,
                Cerebellar_1y = ?,
                Cerebellar_2x = ?,
                Cerebellar_2y = ?,
                State = 4
                WHERE Id = ?;
            """
        try:
            self.cursor.execute(table_update, (Cerebellar_1x, Cerebellar_1y, Cerebellar_2x, Cerebellar_2y, InstanceId))
            return True
        except sqlite3.Error as err:
            print('\033[1;35mUPDATE Cerebellar ', InstanceId, err, '. \033[0m')
            return False

    ## UPDATE Biparietal Information from _seg_info.json
    def update_instance_biparietal(self, InstanceId, Biparietal_1x, Biparietal_1y, Biparietal_2x, Biparietal_2y) -> bool:
        table_update = f"""
                UPDATE instance
                SET Biparietal_1x = ?,
                Biparietal_1y = ?,
                Biparietal_2x = ?,
                Biparietal_2y = ?,
                State = 4
                WHERE Id = ?;
            """
        try:
            self.cursor.execute(table_update, (Biparietal_1x, Biparietal_1y, Biparietal_2x, Biparietal_2y, InstanceId))
            return True
        except sqlite3.Error as err:
            print('\033[1;35mUPDATE Biparietal ', InstanceId, err, '. \033[0m')
            return False
