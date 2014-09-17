
import utils

class TableMapper(object):
    """ metaclass to create readonly ORM class"""
    def __init__(self, table_name):
        self.table_name = table_name

    def __call__(self, classname, base_types, dict):
        def get_col(col):
            return lambda self: self.row[col]

        con = utils.connect_db()
        for col in utils.tablecols(con, self.table_name):
            if col not in dict:
                dict[col] = property(get_col(col))

        return type(classname, base_types, dict)

class Ship(object):
    __metaclass__ = TableMapper('ship_view')
    def __init__(self, con, ship_id):
        cur = con.cursor()
        cur.execute(u'select * from ship_view where id=?', (ship_id,))
        row = cur.fetchone()
        self.row = row # for metaclass

class Deck(object):
    __metaclass__ = TableMapper('api_deck_port')
    def __init__(self, con, row):
        self.con = con
        self.row = row # for metalass

    def ships(self):
        return [None if ship_id == -1 else
                Ship(self.con, ship_id) for ship_id in self.api_ship]

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
        return Deck(self.con, row)
