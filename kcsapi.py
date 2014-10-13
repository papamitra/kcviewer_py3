#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3
import pickle
import re
import simplejson
import utils
import db
import threading
import Queue

def get_cols(con, table_name):
    cur = con.cursor()
    cur.execute(u'select * from ' + table_name)
    return [col[0] for col in cur.description]

class KcsApi(object):

    def __init__(self):
        super(KcsApi, self).__init__()

    def initialize(self):
        #call this function under same thread that invoke dispatch()

        db.initialize()

        self.debug_con = utils.connect_debug_db()
        self.con = utils.connect_db()

        self.tables = [r[0] for r in self.con.execute(u'select name from sqlite_master where type="table";')]
        self.table_cols = {t:get_cols(self.con, t) for t in self.tables}

    def parse_response(self, msg):
        """ http raw response to ApiMessage"""

        try:
            res = msg.response
            req = msg.request
            if re.search("application/json", res.headers["Content-Type"][0]):
                return (req.path, res.content)
            elif re.search("text/plain", res.headers["Content-Type"][0]):
                if 0 == res.content.index("svdata="):
                    return (req.path, res.content[len("svdata="):])
        except Exception, e:
                print(e)

        return None

    def debug_out(self, path, json):
        """ insert ApiMessage into debug DB """

        sql = u"insert into msg values (datetime('now'), ? , ?)"
        self.debug_con.execute(sql, (path, sqlite3.Binary(pickle.dumps(json))))

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

        (path, data) = msg

        try:
            json = simplejson.loads(data)
        except Exception as e:
            print(e)
            return

        if debug_out:
            self.debug_out(path, json)

        if path == u'/kcsapi/api_start2':
            try:
                with self.con:
                    self.insert_or_replace('api_mst_ship', json['api_data']['api_mst_ship'])
                    self.insert_or_replace('api_mst_slotitem', json['api_data']['api_mst_slotitem'])
            except Exception, e:
                print("dispatch failed: " + str(e))

        elif path == u'/kcsapi/api_port/port':
            try:
                with self.con:
                    self.insert_or_replace('api_ship', json['api_data']['api_ship'])
                    self.insert_or_replace('api_deck_port', json['api_data']['api_deck_port'])
            except Exception, e:
                print("%s failed: %s" % (path, str(e)))

        elif path == u'/kcsapi/api_get_member/slot_item':
            try:
                with self.con:
                    self.insert_or_replace('api_slotitem', json['api_data'])
            except Exception, e:
                print("%s failed: %s" % (path, str(e)))

        elif path == u'/kcsapi/api_get_member/ship2':
            try:
                with self.con:
                    self.insert_or_replace('api_ship', json['api_data'])
            except Exception, e:
                print("%s failed: %s" % (path, str(e)))

class KcsApiThread(KcsApi, threading.Thread):
    def __init__(self, on_dispatch = None):
        super(KcsApiThread, self).__init__()

        self.input_queue = Queue.Queue()
        self.on_dispatch = on_dispatch

    def request_dispatch(self, msg):
        api_msg = self.parse_response(msg)
        if api_msg:
            self.input_queue.put(api_msg)

    def stop(self):
        self.input_queue.put(None)
        self.join()

    def run(self):
        self.initialize()

        print('ApiThread start...')
        while True:
            d = self.input_queue.get()
            if d is None:
                break
            self.dispatch(d)
            if self.on_dispatch:
                (path, _) = d
                self.on_dispatch(path)

        print('ApiThread ...done')

# for debug
def parse_debug_db(dbname = None, where = None):
    con = utils.connect_debug_db(dbname)
    c = con.cursor()
    c.execute('select * from msg' + (where if where else ''))
    debug_data = [(row[0], row[1], pickle.loads(str(row[2]))) for row in c]
    con.close()
    return debug_data
