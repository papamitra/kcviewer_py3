#!/usr/bin/env python

import sqlite3

from ship_status import Ui_Form
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QSizePolicy

def parse_db_intlist(l):
    return [int(i) for i in l.split(';')]

class DeckStatus(QWidget):
    def __init__(self, con):
        super(DeckStatus, self).__init__()
        self.con = con
        self.con.row_factory = sqlite3.Row
        self.vbox_layout = QVBoxLayout()
        self.setLayout(self.vbox_layout)
        self.ui_list = []

        for _ in range(6):
            ui = ShipStatus()
            self.ui_list.append(ui)
            self.vbox_layout.addWidget(ui)

    def on_status_change(self):
        cur = self.con.cursor()
        cur.execute(u'select * from api_deck_port where api_id == 1;')
        ship_ids = parse_db_intlist(cur.fetchone()['api_ship'])
        for (i,ship_id) in enumerate(ship_ids):
            ui = self.ui_list[i]
            cur.execute(u'select * from ship_view where id == ?;', [ship_id])
            r = cur.fetchone()
            ui.ship_name.setText(r['name'])
            ui.ship_hp.setText("HP: %d / %d" % (r['nowhp'], r['maxhp']))
            ui.hp_bar.setValue(float(r['nowhp']) / float(r['maxhp']) * 100)
            ui.ship_lv.setText("Lv: %d" % r['lv'])

class ShipStatus(QWidget,Ui_Form):
    def __init__(self, parent=None):
        super(ShipStatus, self).__init__(parent)
        self.setupUi(self)
        self.show()

if __name__ == '__main__':
    import sys

    con = sqlite3.connect('data.db')

    app = QApplication(sys.argv)

    st = DeckStatus(con)
    st.on_status_change()
    st.show()

    sys.exit(app.exec_())
