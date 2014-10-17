
import utils
import db

db.initialize()

class TableMapper(object):
    """ metaclass to create readonly ORM class"""
    def __init__(self, table_name, sql):
        self.table_name = table_name
        self.sql = sql

    def __call__(self, classname, base_types, dict):
        def init(s, con, id=None, row=None):
            s._con = con
            if row is None:
                cur = s._con.cursor()
                cur.execute(self.sql, (id,))
                row = cur.fetchone()
            s._row = row

        def get_col(col):
            return lambda self: self._row[col]

        con = utils.connect_db()
        for col in utils.tablecols(con, self.table_name):
            if col not in dict:
                dict[col] = property(get_col(col))

        dict['__init__'] = init
        dict['is_null'] = lambda s: s._row is None

        return type(classname, base_types, dict)

class Ship(object):
    __metaclass__ = TableMapper('ship_view', u'select * from ship_view where id=?')

    def cond_state(self):
        if self.cond <= 20:
            return 'serious tired'
        elif self.cond <= 29:
            return 'middle tired'
        elif self.cond <= 39:
            return 'slight tired'
        elif self.cond <= 49:
            return 'normal'
        return 'good'

    @staticmethod
    def _supply_state(rate):
        if rate <= 0.3:
            return 'empty'
        elif rate <= 0.7:
            return 'half'
        elif rate < 1.0:
            return 'normal'
        else:
            return 'full'

    def fuel_state(self):
        return self._supply_state(self.fuel_rate())

    def fuel_rate(self):
        return float(self.fuel) / float(self.fuel_max)

    def bull_state(self):
        return self._supply_state(self.bull_rate())

    def bull_rate(self):
        return float(self.bull) / float(self.bull_max)

class Deck(object):
    __metaclass__ = TableMapper('api_deck_port', u'select * from api_deck_port where api_id = ?')

    def ships(self):
        return [None if ship_id == -1 else
                Ship(self._con, ship_id) for ship_id in self.api_ship]

    def state(self):
        if self.api_mission[1] != 0:
            return 'expedition'

        for ship in self.ships():
            if ship is None: continue
            if ship.fuel_rate() < 1.0 or \
               ship.bull_rate() < 1.0:
                return 'not ready'

        return 'ready'

class SlotItem(object):
    __metaclass__ = TableMapper('slotitem_view', u'select * from slotitem_view where id=?')

class Port(object):
    def __init__(self, con):
        self.con = con

    def decks(self):
        cur = self.con.cursor()
        cur.execute(u'select * from api_deck_port')
        return [Deck(self.con, row=row) for row in cur]

    def deck(self, deck_id):
        return Deck(self.con, deck_id)
