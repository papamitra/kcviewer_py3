
import utils

def impl_shipstatus(classname, base_types, dict):
    def get_col(col):
        return lambda self: self.row[col]

    con = utils.connect_db()
    for col in utils.tablecols(con, 'ship_view'):
        if col not in dict:
            dict[col] = property(get_col(col))

    return type(classname, base_types, dict)

class ShipStatus(object):
    __metaclass__ = impl_shipstatus
    def __init__(self, row):
        self.row = row

    @staticmethod
    def new(con, ship_id):
        cur = con.cursor()
        cur.execute(u'select * from ship_view where id=?', (ship_id,))
        row = cur.fetchone()
        return ShipStatus(row)
