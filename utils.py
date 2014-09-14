
import sqlite3

IntList = list
sqlite3.register_adapter(IntList, lambda l: ';'.join([str(i) for i in l]))
sqlite3.register_converter("IntList", lambda s: [int(i) for i in s.split(';')])

def connect_db():
    con = sqlite3.connect('data.db', detect_types = sqlite3.PARSE_DECLTYPES)
    con.row_factory = sqlite3.Row
    return con

def tablecols(con, table_name):
    cur = con.cursor()
    cur.execute(u'select * from ' + table_name)
    return [col[0] for col in cur.description]
