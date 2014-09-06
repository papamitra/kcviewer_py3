#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3
import pickle
import re
import simplejson

DEBUG_DB = "kscapi_debug.db"
CREATE_MESSAGE_TABLE = u"""
create table if not exists msg(
  timestamp integer,
  path text,
  data blob
);
"""

class ApiMessage(object):
    def __init__(self, path, json):
        self.path = path
        self.json = json

class KcsApi(object):

    def __init__(self):
        self.debug_con = sqlite3.connect(DEBUG_DB, isolation_level=None)
        self.debug_con.execute(CREATE_MESSAGE_TABLE)

    @staticmethod
    def parse_respose(msg):
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
        sql = u"insert into msg values (datetime('now'), ? , ?)"
        self.debug_con.execute(sql, (msg.path, sqlite3.Binary(pickle.dumps(msg.json))))

    def dispatch(self, msg):
        self.debug_out(msg)


# for debug
def parse_debug_db(where = None):
    con = sqlite3.connect(DEBUG_DB)
    c = con.cursor()
    c.execute('select * from msg' + (where if where else ''))
    debug_data = [(row[0], row[1], pickle.loads(str(row[2]))) for row in c]
    con.close()
    return debug_data
