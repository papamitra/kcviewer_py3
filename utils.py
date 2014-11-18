# -*- coding: utf-8 -*-

import sqlite3

IntList = list
sqlite3.register_adapter(IntList, lambda l: ';'.join([str(i) for i in l]))
sqlite3.register_converter('IntList', lambda s: [int(i) for i in str(s, encoding='utf-8').split(';')])

def connect_db():
    con = sqlite3.connect('data.db', detect_types = sqlite3.PARSE_DECLTYPES)
    con.row_factory = sqlite3.Row
    return con

def connect_debug_db(dbname = None):
    if dbname is None:
        dbname = 'kcsapi_debug.db'
    con = sqlite3.connect(dbname, isolation_level=None)
    con.row_factory = sqlite3.Row
    return con

def tablecols(con, table_name):
    cur = con.cursor()
    cur.execute('select * from ' + table_name)
    return [col[0] for col in cur.description]
