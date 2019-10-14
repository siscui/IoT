from sqlite3 import connect, Error
from time import time
from os import sys


class DbConnection:
    def __init__(self, db_name):
        self.conn = connect(db_name)

        try:
            cur = self.conn.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS FIRESTORE_DOCS \
                (ID INTEGER PRIMARY KEY AUTOINCREMENT, DOC_ID TEXT, PLANT TEXT, TIME TEXT)")
            cur.execute("CREATE TABLE IF NOT EXISTS TEMPERATURE \
                (ID INTEGER PRIMARY KEY AUTOINCREMENT, VALUE NUMERIC, STATUS TEXT, TIME TEXT, UPLOADED INTEGER)")
            cur.execute("CREATE TABLE IF NOT EXISTS HUMIDITY \
                (ID INTEGER PRIMARY KEY AUTOINCREMENT, VALUE NUMERIC, STATUS TEXT, TIME TEXT, UPLOADED INTEGER)")
            cur.execute("CREATE TABLE IF NOT EXISTS ILLUMINATION \
                (ID INTEGER PRIMARY KEY AUTOINCREMENT, VALUE NUMERIC, STATUS TEXT, TIME TEXT, UPLOADED INTEGER)")
            cur.execute("CREATE TABLE IF NOT EXISTS PLANT \
                (ID INTEGER PRIMARY KEY AUTOINCREMENT, SPECIES TEXT, MATURITY INTEGER, TIME TEXT, UPLOADED INTEGER)")
        except Error as e:
            sys.exit(e)

    def save(self, table, obj):
        keys = ", ".join(obj.keys())
        args = ", ".join(list(map(lambda x: "?", obj.keys())))
        timestamp = int(time())
        values = list(obj.values())
        values.append(timestamp)
        with self.conn:
            self.conn.execute(f"INSERT INTO {table} ({keys}, TIME) VALUES ({args}, ?)", values)
        return timestamp

    def get(self, table, query):
        cur = self.conn.cursor()
        cur.execute(f"SELECT * FROM {table} WHERE {query}")
        return cur.fetchall()

    def set(self, table, obj, query):
        cur = self.conn.cursor()
        data = ", ".join(list(map(lambda x: f"{x} = {obj[x]}", obj)))
        print(data)
        print(f"UPDATE {table} SET {data} WHERE {query}")
        cur.execute(f"UPDATE {table} SET {data} WHERE {query}")
        self.conn.commit()

