import sqlite3
from sqlite3 import Error

from database.environmental import Environmental
from database.financial import Financial
from database.political import Political


class DBDude:
    def __init__(self, db_file):
        self.db_file = db_file

    def create_connection(self):
        try:
            conn = sqlite3.connect(self.db_file)
            return conn
        except Error as e:
            print(e)

    def create_table(self, create_table_sql):
        conn = self.create_connection()
        try:
            c = conn.cursor()
            c.execute(create_table_sql)
        except Error as e:
            print(e)

    ###################################################################################
    # ----------------------------- ENVIRONMENTAL -------------------------------------
    ###################################################################################
    def create_environmental(self, environmental: Environmental):
        conn = self.create_connection()
        with conn:
            sql = ''' INSERT INTO environmental(name,pretty_name,base_value,increment,retrieval)
                      VALUES(?,?,?,?,?) '''
            cur = conn.cursor()
            cur.execute(sql, environmental.to_tuple_insert())
            return cur.lastrowid

    def select_all_environmental(self):
        conn = self.create_connection()
        with conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM environmental")
            return [Environmental.from_tuple(d) for d in cur.fetchall()]

    def delete_all_environmental(self):
        conn = self.create_connection()
        with conn:
            sql = 'DELETE FROM environmental'
            cur = conn.cursor()
            cur.execute(sql)

    ###################################################################################
    # -------------------------------- POLITICAL --------------------------------------
    ###################################################################################
    def create_political_if_not_exists(self, political: Political):
        conn = self.create_connection()
        with conn:
            sql = ''' INSERT OR IGNORE INTO political(external_id, title, summary, feed, published)
                      VALUES(?,?,?,?,?) '''
            cur = conn.cursor()
            cur.execute(sql, political.to_tuple_insert())
            return cur.lastrowid

    def select_all_political(self):
        conn = self.create_connection()
        with conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM political")
            return [Political.from_tuple(d) for d in cur.fetchall()]

    ###################################################################################
    # -------------------------------- FINANCIAL --------------------------------------
    ###################################################################################
    def create_financial(self, financial: Financial):
        conn = self.create_connection()
        with conn:
            sql = ''' INSERT INTO financial(symbol, company, type, industry, price, currency, change, timestamp)
                      VALUES(?,?,?,?,?,?,?,?) '''
            cur = conn.cursor()
            cur.execute(sql, financial.to_tuple_insert())
            return cur.lastrowid

    def select_all_financial(self):
        conn = self.create_connection()
        with conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM financial WHERE price != 0")
            return [Financial.from_tuple(d) for d in cur.fetchall()]

    def select_all_financial_private(self):
        conn = self.create_connection()
        with conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM financial WHERE type = 'private'")
            return [Financial.from_tuple(d) for d in cur.fetchall()]

    def select_all_financial_public(self):
        conn = self.create_connection()
        with conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM financial WHERE type = 'public'")
            return [Financial.from_tuple(d) for d in cur.fetchall()]

    def update_financial(self, financial_update):
        conn = self.create_connection()
        with conn:
            sql = ''' UPDATE financial
                      SET price = ? ,
                          change = ? ,
                          timestamp = ?
                      WHERE company = ?'''
            cur = conn.cursor()
            cur.execute(sql, financial_update)
            return cur.lastrowid
