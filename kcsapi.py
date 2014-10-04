#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3
import pickle
import re
import simplejson
import utils
import db

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
        db.initialize()

        self.debug_con = utils.connect_debug_db()
        self.con = utils.connect_db()

        self.tables = [r[0] for r in self.con.execute(u'select name from sqlite_master where type="table";')]
        self.table_cols = {t:get_cols(self.con, t) for t in self.tables}

    @staticmethod
    def parse_respose(msg):
        """ http raw response to ApiMessage"""

        try:
            res = msg.response
            req = msg.request
            if re.search("application/json", res.headers["Content-Type"][0]):
                js = simplejson.loads(res.content)
                return ApiMessage(req.path, js)
            elif re.search("text/plain", res.headers["Content-Type"][0]):
                if 0 == res.content.index("svdata="):
                    js = simplejson.loads(res.content[len("svdata="):])
                    return ApiMessage(req.path, js)
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
                    self.insert_or_replace('api_mst_ship', msg.json['api_data']['api_mst_ship'])
                    self.insert_or_replace('api_mst_slotitem', msg.json['api_data']['api_mst_slotitem'])
            except Exception, e:
                print("dispatch failed: " + str(e))

        elif msg.path == u'/kcsapi/api_port/port':
            try:
                with self.con:
                    self.insert_or_replace('api_ship', msg.json['api_data']['api_ship'])
                    self.insert_or_replace('api_deck_port', msg.json['api_data']['api_deck_port'])
            except Exception, e:
                print("%s failed: %s" % (msg.path, str(e)))

        elif msg.path == u'/kcsapi/api_get_member/slot_item':
            try:
                with self.con:
                    self.insert_or_replace('api_slotitem', msg.json['api_data'])
            except Exception, e:
                print("%s failed: %s" % (msg.path, str(e)))

# for debug
def parse_debug_db(where = None):
    con = utils.connect_debug_db()
    c = con.cursor()
    c.execute('select * from msg' + (where if where else ''))
    debug_data = [(row[0], row[1], pickle.loads(str(row[2]))) for row in c]
    con.close()
    return debug_data
