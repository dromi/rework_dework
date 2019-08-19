import sqlite3
from sqlite3 import Error

from database.environmental import Environmental
from database.financial import Financial
from database.political import Political


class DBDude:
    def __init__(self):
        self.db_file = 'dework.db'

    def create_connection(self):
        """ create a database connection to a SQLite database """
        try:
            conn = sqlite3.connect(self.db_file)
            return conn
        except Error as e:
            print(e)

    def create_table(self, create_table_sql):
        """ create a table from the create_table_sql statement
        :param conn: Connection object
        :param create_table_sql: a CREATE TABLE statement
        :return:
        """
        conn = self.create_connection()
        try:
            c = conn.cursor()
            c.execute(create_table_sql)
        except Error as e:
            print(e)

    def create_enviromental(self, environmental: Environmental):
        """
        Create a new enviromental into the enviromental table
        :param conn:
        :param environmental:
        :return: project id
        """
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
        """
        Delete all rows in the tasks table
        :param conn: Connection to the SQLite database
        :return:
        """
        conn = self.create_connection()
        with conn:
            sql = 'DELETE FROM environmental'
            cur = conn.cursor()
            cur.execute(sql)

    def create_political_if_not_exists(self, political: Political):
        """
        Create a new political into the political table
        :param conn:
        :param political:
        :return: project id
        """
        conn = self.create_connection()
        with conn:
            sql = ''' INSERT OR IGNORE INTO political(external_id, title, summary, feed, published)
                      VALUES(?,?,?,?,?) '''
            cur = conn.cursor()
            cur.execute(sql, political.to_tuple_insert())
            return cur.lastrowid

    def create_financial(self, financial: Financial):
        """
        Create a new political into the political table
        :param conn:
        :param financial:
        :return: project id
        """
        conn = self.create_connection()
        with conn:
            sql = ''' INSERT INTO financial(symbol, name, price, change, timestamp)
                      VALUES(?,?,?,?,?) '''
            cur = conn.cursor()
            cur.execute(sql, financial.to_tuple_insert())
            return cur.lastrowid
