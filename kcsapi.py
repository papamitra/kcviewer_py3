#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3
import pickle
import re
import simplejson
import threading
import Queue

import model
import utils
import db

def get_cols(con, table_name):
    cur = con.cursor()
    cur.execute(u'select * from ' + table_name)
    return [col[0] for col in cur.description]

class KcsCommand(object):
    RESPONSE='response'
    REQUEST='request'

    command_table = {}

    def __init__(self, direction, path):
        self.direction = direction
        self.path = path

    def __call__(self, classname, base_types, dict):
        dict['dir'] = self.direction
        t = type(classname, base_types, dict)
        self.command_table[(self.direction, self.path)] = t
        return t

class ApiReqUnknown(object):
    def __init__(self, path, content):
        self.path = path
        self.dir = KcsCommand.REQUEST
        self._cntent = content

    def execute(self):
        try:
            request = urlparse.parse_qs(self._content)
        except Exception as e:
            return

        KcsDb.debug_out(KcsCommand.REQUEST, self.path, request)

class ApiResUnknown(object):
    def __init__(self, path, content):
        self.path = path
        self.dir = KcsCommand.RESPONSE
        self._cntent = content

    def execute(self):
        try:
            json = simplejson.loads(self._content)
        except Exception as e:
            return

        KcsDb.debug_out(KcsCommand.RESPONSE, self.path, json)

class KcsDb(object):
    con = None
    debug_con = None
    tables = []
    table_cols = {}

    @classmethod
    def initialize(cls):
        #call this function under same thread that invoke dispatch()

        db.initialize()

        cls.debug_con = utils.connect_debug_db()
        cls.con = utils.connect_db()

        cls.tables = [r[0] for r in cls.con.execute(u'select name from sqlite_master where type="table";')]
        cls.table_cols = {t:get_cols(cls.con, t) for t in cls.tables}

    @classmethod
    def debug_out(cls, msgtype, path, json):
        """ insert ApiMessage into debug DB """

        sql = u"insert into msg values (datetime('now'), ?, ? , ?)"
        cls.debug_con.execute(sql, (path, msgtype, sqlite3.Binary(pickle.dumps(json))))

    @classmethod
    def insert_or_replace(cls, table_name, data, conv={}):
        """ insert json data into table with data converting if needed """

        cols = cls.table_cols[table_name]
        sql = u"""
        insert or replace into {table_name} ({col_names}) values ({val_holders})
        """.format(table_name  = table_name,
                   col_names   = ','.join(cols),
                   val_holders = ','.join(['?'] * len(cols)))

        cls.con.executemany(sql,
                             [[d[c] if not c in conv else conv[c](d) for c in cols] for d in data])

class KcsApi(object):
    import command

    def __init__(self):
        super(KcsApi, self).__init__()

    def parse_response(self, path, content_type, content):
        """ parse http raw response"""

        try:
            print('res: ', path)
            if re.search("application/json", content_type):
                command = KcsCommand.command_table.get((KcsCommand.RESPONSE, path), ApiResUnknown)
                return command(path, content)
            elif re.search("text/plain", content_type):
                if 0 == content.index("svdata="):
                    command = KcsCommand.command_table.get((KcsCommand.RESPONSE, path), ApiResUnknown)
                    return command(path, content[len("svdata="):])
        except Exception, e:
                print(e)

        return None

    def parse_request(self, path, content_type, content):
        """ parse http raw request"""

        try:
            print('req: ', path)
            if re.search('application/x-www-form-urlencoded', content_type):
                command = KcsCommand.command_table.get((KcsCommand.REQUEST, path), ApiReqUnknown)
                return command(path, content)
        except Exception, e:
                print(e)

        return None

class KcsApiThread(KcsApi, threading.Thread):
    def __init__(self, on_dispatch = None):
        super(KcsApiThread, self).__init__()

        self.input_queue = Queue.Queue()
        self.on_dispatch = on_dispatch

    def on_response(self, path, content_type, content):
        res_cmd = self.parse_response(path, content_type, content)
        if res_cmd:
            self.input_queue.put(res_cmd)

    def on_request(self, path, content_type, content):
        req_cmd = self.parse_request(path, content_Type, content)
        if req_cmd:
            self.input_queue.put(req_cmd)
        pass

    def stop(self):
        self.input_queue.put(None)
        self.join()

    def run(self):
        KcsDb.initialize()

        print('ApiThread start...')
        while True:
            cmd = self.input_queue.get()
            if cmd is None: break
            try:
                cmd.execute()
            except Exception as e:
                print(type(cmd), e)

            if self.on_dispatch:
                self.on_dispatch(cmd.dir, cmd.path)

        print('ApiThread ...done')

# for debug
def parse_debug_db(dbname = None, where = None):
    con = utils.connect_debug_db(dbname)
    c = con.cursor()
    c.execute('select * from msg' + (where if where else ''))
    debug_data = [(row[0], row[1], row[2], pickle.loads(str(row[3]))) for row in c]
    con.close()
    return debug_data
