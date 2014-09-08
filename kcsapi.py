#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3
import pickle
import re
import simplejson
import UserList

def intlist_to_text(key):
    return lambda d: ';'.join(str(i) for i in d[key])

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

CREATE_SHIP_TABLE = u"""
create table if not exists api_ship(
  api_id      integer primary key,
  api_ship_id integer,
  api_lv      integer,
  api_bull    integer,
  api_fuel    integer,
  api_cond    integer,
  api_nowhp   integer,
  api_maxhp   integer,
  api_slot    text,
  foreign key(api_ship_id) references api_mst_ship(api_id)
);
"""

ADAPT_SHIP = {'api_slot': intlist_to_text('api_slot')}

CREATE_DECK_PORT_TABLE = u"""
create table if not exists api_deck_port(
  api_id      integer primary key,
  api_mission text,
  api_name    text,
  api_ship    text
);
"""

ADAPT_DECK_PORT = {'api_mission' : intlist_to_text('api_mission'),
                   'api_ship'    : intlist_to_text('api_ship')}

CREATE_SHIP_VIEW = u"""
create view if not exists ship_view as
select api_ship.api_id        as id,
       api_mst_ship.api_name  as name,
       api_ship.api_lv        as lv,
       api_ship.api_fuel      as fuel,
       api_ship.api_bull      as bull,
       api_ship.api_cond      as cond,
       api_ship.api_nowhp     as nowhp,
       api_ship.api_maxhp     as maxhp,
       api_ship.api_slot      as slot
from api_ship left join api_mst_ship on api_ship.api_ship_id == api_mst_ship.api_id;
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
            self.con.execute(CREATE_SHIP_TABLE)
            self.con.execute(CREATE_DECK_PORT_TABLE)
            self.con.execute(CREATE_SHIP_VIEW)

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

        elif msg.path == u'/kcsapi/api_port/port':
            try:
                with self.con:
                    ships = msg.json['api_data']['api_ship']
                    self.insert_or_replace('api_ship', ships, ADAPT_SHIP)

                    port =  msg.json['api_data']['api_deck_port']
                    self.insert_or_replace('api_deck_port', port, ADAPT_DECK_PORT)

            except Exception, e:
                print("%s failed: %s" % (msg.path, str(e)))

# for debug
def parse_debug_db(where = None):
    con = sqlite3.connect(DEBUG_DB)
    c = con.cursor()
    c.execute('select * from msg' + (where if where else ''))
    debug_data = [(row[0], row[1], pickle.loads(str(row[2]))) for row in c]
    con.close()
    return debug_data
