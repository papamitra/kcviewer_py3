
import utils
import db

db.initialize()

class TableMapper(object):
    """ metaclass to create readonly ORM class"""
    def __init__(self, table_name, sql = None):
        self.table_name = table_name
        self.sql = sql

    def __call__(self, classname, base_types, dict):
        def init(s, con, ident):
            cur = con.cursor()
            cur.execute(self.sql, (ident,))
            row = cur.fetchone()
            s._row = row

        def get_col(col):
            return lambda self: self._row[col]

        con = utils.connect_db()
        for col in utils.tablecols(con, self.table_name):
            if col not in dict:
                dict[col] = property(get_col(col))

        if self.sql:
            dict['__init__'] = init

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
    __metaclass__ = TableMapper('api_deck_port')
    def __init__(self, con, row):
        self.con = con
        self._row = row # for metalass

    def ships(self):
        return [None if ship_id == -1 else
                Ship(self.con, ship_id) for ship_id in self.api_ship]

class SlotItem(object):
    __metaclass__ = TableMapper('slotitem_view', u'select * from slotitem_view where id=?')

class Port(object):
    def __init__(self, con):
        self.con = con

    def decks(self):
        cur = self.con.cursor()
        cur.execute(u'select * from api_deck_port')
        return [Deck(self.con, row) for row in cur]

    def deck(self, deck_id):
        cur = self.con.cursor()
        cur.execute(u'select * from api_deck_port where api_id = ?', (deck_id, ))
        row = cur.fetchone()
        if row is None:
            return None
        return Deck(self.con, row)
