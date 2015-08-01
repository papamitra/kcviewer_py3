# -*- coding: utf-8 -*-

from kcsapi import KcsDb
from kcsapi import KcsCommand
import simplejson
import urllib.parse
import model

class ApiStart2(object, metaclass=KcsCommand(KcsCommand.RESPONSE, '/kcsapi/api_start2')):
    def __init__(self, path, content):
        self.path = path
        self._content = content

    def execute(self):
        json = simplejson.loads(self._content)

        KcsDb.debug_out(self.dir, self.path, json)

        with KcsDb.con:
            KcsDb.insert_or_replace('api_mst_ship', json['api_data']['api_mst_ship'])
            KcsDb.insert_or_replace('api_mst_slotitem', json['api_data']['api_mst_slotitem'])


class ApiPort(object, metaclass=KcsCommand(KcsCommand.RESPONSE, '/kcsapi/api_port/port')):
    def __init__(self, path, content):
        self.path = path
        self._content = content
    def execute(self):
        json = simplejson.loads(self._content)

        KcsDb.debug_out(self.dir, self.path, json)

        with KcsDb.con:
            KcsDb.insert_or_replace('api_ship', json['api_data']['api_ship'])
            KcsDb.insert_or_replace('api_deck_port', json['api_data']['api_deck_port'])


class ApiSlotItem(object, metaclass=KcsCommand(KcsCommand.RESPONSE, '/kcsapi/api_get_member/slot_item')):
    def __init__(self, path, content):
        self.path = path
        self._content = content

    def execute(self):
        json = simplejson.loads(self._content)

        KcsDb.debug_out(self.dir, self.path, json)

        with KcsDb.con:
            KcsDb.insert_or_replace('api_slotitem', json['api_data'])

class ApiShip2(object, metaclass=KcsCommand(KcsCommand.RESPONSE, '/kcsapi/api_get_member/ship2')):
    def __init__(self, path, content):
        self.path = path
        self._content = content

    def execute(self):
        json = simplejson.loads(self._content)

        KcsDb.debug_out(self.dir, self.path, json)

        with KcsDb.con:
            KcsDb.insert_or_replace('api_ship', json['api_data'])

class ApiShipDeck(object, metaclass=KcsCommand(KcsCommand.RESPONSE, '/kcsapi/api_get_member/ship_deck')):
    def __init__(self, path, content):
        self.path = path
        self._content = content

    def execute(self):
        json = simplejson.loads(self._content)

        KcsDb.debug_out(self.dir, self.path, json)

        with KcsDb.con:
            KcsDb.insert_or_replace('api_ship', json['api_data']['api_ship_data'])


class ApiReqHensei(object, metaclass=KcsCommand(KcsCommand.REQUEST, '/kcsapi/api_req_hensei/change')):
    def __init__(self, path, content):
        self.path = path
        self._content = content

    def execute(self):
        request = urllib.parse.parse_qs(self._content)

        KcsDb.debug_out(self.dir, self.path, request)

        deck_id = int(request['api_id'][0])
        ship_id = int(request['api_ship_id'][0])
        if ship_id < -2:
            print(('invalid shipid:{0}'.format(ship_id)))
            return
        pos_idx = int(request['api_ship_idx'][0]) # ship pos idx in fleet

        port = model.Port(KcsDb.con)
        deck = port.deck(deck_id)
        ships = list(deck.api_ship)
        if ship_id == -2:
            ships = ships[:1] + [-1] * (len(ships) -1)
        elif ship_id == -1:
            num = len(ships)
            ships[pos_idx] = ship_id
            if -1 in ships: ships.remove(-1)
            ships += [-1] * (num - len(ships))
        else:
            if ship_id in ships:
                num = len(ships)
                exchange = ships[pos_idx]
                ships[ships.index(ship_id)] = exchange
                if -1 in ships: ships.remove(-1)
                ships += [-1] * (num - len(ships))
            ships[pos_idx] = ship_id
        with KcsDb.con:
            KcsDb.con.execute('update api_deck_port set api_ship=? where api_id=?',
                              (ships, deck_id))

class ApiReqUnsetSlotAll(object, metaclass=KcsCommand(KcsCommand.REQUEST, '/kcsapi/api_req_kaisou/unsetslot_all')):
    def __init__(self, path, content):
        self.path = path
        self._content = content

    def execute(self):
        request = urllib.parse.parse_qs(self._content)

        KcsDb.debug_out(self.dir, self.path, request)

        ship_id = int(request['api_id'][0])
        ship = model.Ship(KcsDb.con, ship_id)
        slot = [-1] * len(ship.slot)
        with KcsDb.con:
            KcsDb.con.execute('update api_ship set api_slot=? where api_id=?',
                              (slot, ship_id))

class ApiReqSlotSet(object, metaclass=KcsCommand(KcsCommand.REQUEST, '/kcsapi/api_req_kaisou/slotset')):
    def __init__(self, path, content):
        self.path = path
        self._content = content

    def execute(self):
        request = urllib.parse.parse_qs(self._content)

        KcsDb.debug_out(self.dir, self.path, request)

        ship_id = int(request['api_id'][0])
        item_id = int(request['api_item_id'][0])
        slot_idx = int(request['api_slot_idx'][0])
        ship = model.Ship(KcsDb.con, ship_id)
        slot = ship.slot
        slot[slot_idx] = item_id
        with KcsDb.con:
            KcsDb.con.execute('update api_ship set api_slot=? where api_id=?',
                              (slot, ship_id))

class ApiReqCharge(object, metaclass=KcsCommand(KcsCommand.REQUEST, '/kcsapi/api_req_hokyu/charge')):
    def __init__(self, path, content):
        self.path = path
        self._content = content

    def execute(self):
        request = urllib.parse.parse_qs(self._content)

        KcsDb.debug_out(self.dir, self.path, request)

        ships = [int(i) for i  in request['api_id_items'][0].split(',')]
        kind = int(request['api_kind'][0])
        with KcsDb.con:
            if kind==1 or kind==3:
                KcsDb.con.executemany(
                    'update api_ship set api_fuel=(select fuel_max from ship_view where id=?) where api_id=?',
                    [(sid, sid) for sid in ships])

            if kind==2 or kind==3:
                KcsDb.con.executemany(
                    'update api_ship set api_bull=(select bull_max from ship_view where id=?) where api_id=?',
                    [(sid, sid) for sid in ships])
