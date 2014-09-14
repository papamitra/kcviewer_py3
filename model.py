
import utils

class DbMapper(object):
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

class ShipStatus(object):
    __metaclass__ = DbMapper('ship_view')
    def __init__(self, con, ship_id):
        cur = con.cursor()
        cur.execute(u'select * from ship_view where id=?', (ship_id,))
        row = cur.fetchone()
        self.row = row

class DeckPortInfo(object):
    __metaclass__ = DbMapper('api_deck_port')
    def __init__(self, con, port_id):
        self.con = con
        cur = self.con.cursor()
        cur.execute(u'select * from api_deck_port where api_id=?', (port_id,))
        row = cur.fetchone()
        self.row = row

    def ships(self):
        return [ShipStatus(self.con, ship_id) for ship_id in self.api_ship]
