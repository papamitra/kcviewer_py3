# -*- coding: utf-8 -*-

import sqlite3
import utils

CREATE_MESSAGE_TABLE = u"""
create table if not exists msg(
  timestamp integer,
  path text,
  data blob
);
"""

DATA_DB = 'data.db'

CREATE_MST_SHIP_TABLE = u"""
create table if not exists api_mst_ship(
  api_id integer primary key,
  api_fuel_max integer,
  api_bull_max integer,
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
  api_slot    IntList,
  foreign key(api_ship_id) references api_mst_ship(api_id)
);
"""

CREATE_DECK_PORT_TABLE = u"""
create table if not exists api_deck_port(
  api_id      integer primary key,
  api_mission IntList,
  api_name    text,
  api_ship    IntList
);
"""

CREATE_MST_SLOTITEM_TABLE = u"""
create table if not exists api_mst_slotitem(
  api_id     integer primary key,
  api_name   text,
  api_type   IntList
);
"""

CREATE_SLOTITEM_TABLE = u"""
create table if not exists api_slotitem(
  api_id          integer primary key,
  api_locked      integer,
  api_slotitem_id integer,
  foreign key(api_slotitem_id) references api_mst_slotitem(api_id)
);
"""

CREATE_SHIP_VIEW = u"""
create view if not exists ship_view as
select api_ship.api_id        as id,
       api_mst_ship.api_name  as name,
       api_ship.api_lv        as lv,
       api_ship.api_fuel      as fuel,
       api_ship.api_bull      as bull,
       api_mst_ship.api_bull_max as bull_max,
       api_mst_ship.api_fuel_max as fuel_max,
       api_ship.api_cond      as cond,
       api_ship.api_nowhp     as nowhp,
       api_ship.api_maxhp     as maxhp,
       api_ship.api_slot      as slot
from api_ship left join api_mst_ship on api_ship.api_ship_id == api_mst_ship.api_id;
"""

CREATE_SLOTITEM_VIEW = u"""
create view if not exists slotitem_view as
select api_slotitem.api_id        as id,
       api_mst_slotitem.api_name  as name,
       api_mst_slotitem.api_type  as item_type
from api_slotitem left join api_mst_slotitem on api_slotitem.api_slotitem_id == api_mst_slotitem.api_id;
"""

def initialize():
    debug_con = utils.connect_debug_db()
    debug_con.execute(CREATE_MESSAGE_TABLE)

    con = utils.connect_db()
    with con:
        con.execute(CREATE_MST_SHIP_TABLE)
        con.execute(CREATE_SHIP_TABLE)
        con.execute(CREATE_DECK_PORT_TABLE)
        con.execute(CREATE_MST_SLOTITEM_TABLE)
        con.execute(CREATE_SHIP_VIEW)
        con.execute(CREATE_MST_SLOTITEM_TABLE)
        con.execute(CREATE_SLOTITEM_TABLE)
        con.execute(CREATE_SLOTITEM_VIEW)
