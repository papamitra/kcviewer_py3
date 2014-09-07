#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3
import pickle
import re
import simplejson

DEBUG_DB = 'kscapi_debug.db'
CREATE_MESSAGE_TABLE = u"""
create table if not exists msg(
  timestamp integer,
  path text,
  data blob
);
"""

DATA_DB = 'data.db'
CREATE_MASTER_SHIP_TABLE = u"""
create table if not exists api_mst_ship(
  api_id integer primary key,
  api_name text not null
);
"""

def get_cols(con, table_name):
    cur = con.cursor()
    cur.execute(u'select * from ' + table_name)
    return [col[0] for col in cur.description]

class ApiMessage(object):
    def __init__(self, path, json):
        self.path = path
        self.json = json

class KcsApi(object):

    def __init__(self):
        self.debug_con = sqlite3.connect(DEBUG_DB, isolation_level=None)
        self.debug_con.execute(CREATE_MESSAGE_TABLE)

        self.con = sqlite3.connect(DATA_DB)
        with self.con:
            self.con.execute(CREATE_MASTER_SHIP_TABLE)
            self.mst_ship_cols = get_cols(self.con, 'api_mst_ship')

        self.tables = [r[0] for r in self.con.execute(u'select name from sqlite_master where type="table";')]
        self.table_cols = {t:get_cols(self.con, t) for t in self.tables}

    @staticmethod
    def parse_respose(msg):
        """ http raw response to ApiMessage"""

        try:
            if re.search("application/json", msg.headers["Content-Type"][0]):
                js = simplejson.loads(msg.content)
                return ApiMessage(msg.flow.request.path, js)
            elif re.search("text/plain", msg.headers["Content-Type"][0]):
                if 0 == msg.content.index("svdata="):
                    js = simplejson.loads(msg.content[len("svdata="):])
                    return ApiMessage(msg.flow.request.path, js)
        except Exception, e:
                print(e)

        return None

    def debug_out(self, msg):
        """ insert ApiMessage into debug DB """

        sql = u"insert into msg values (datetime('now'), ? , ?)"
        self.debug_con.execute(sql, (msg.path, sqlite3.Binary(pickle.dumps(msg.json))))

    def insert_or_replace(self, table_name, data, conv={}):
        """ insert json data into table with data converting if needed """

        cols = self.table_cols[table_name]
        sql = u"""
        insert or replace into {table_name} ({col_names}) values ({val_holders})
        """.format(table_name  = table_name,
                   col_names   = ','.join(cols),
                   val_holders = ','.join(['?'] * len(cols)))

        self.con.executemany(sql,
                             [[d[c] if not c in conv else conv[c](d) for c in cols] for d in data])

    def dispatch(self, msg, debug_out=True):
        """ dispatch api message """

        if debug_out:
            self.debug_out(msg)

        if msg.path == u'/kcsapi/api_start2':
            try:
                with self.con:
                    records = msg.json['api_data']['api_mst_ship']
                    self.insert_or_replace('api_mst_ship', records)
            except Exception, e:
                print("dispatch failed: " + str(e))

# for debug
def parse_debug_db(where = None):
    con = sqlite3.connect(DEBUG_DB)
    c = con.cursor()
    c.execute('select * from msg' + (where if where else ''))
    debug_data = [(row[0], row[1], pickle.loads(str(row[2]))) for row in c]
    con.close()
    return debug_data