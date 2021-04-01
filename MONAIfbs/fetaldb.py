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

    ## SELECT State == 1 GROUP BY PseudoAcc
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

    #UPDATE
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

    #UPDATE
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

    #UPDATE
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
