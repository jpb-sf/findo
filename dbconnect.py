import sqlite3
 
class DataBaseConnect(object):
    def __init__(self, db):
        self.conn = sqlite3.connect(db)
        self.conn.row_factory = sqlite3.Row
        self.conn.commit()
        self.cur = self.conn.cursor()
        self.cur.description

    def __del__(self):
        self.conn.close()
