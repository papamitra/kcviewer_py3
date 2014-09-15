#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3

from ship_status import Ui_Form
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QSizePolicy
import utils
import model

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
        deck = model.DeckPortInfo(self.con, 2)
        for (i,ship) in enumerate(deck.ships()):
            ui = self.ui_list[i]
            ui.set_ship(ship)

HP_FORMAT = u'<html><head/><body><p><span style=" font-size:16pt;">HP: </span><span style=" font-size:16pt; font-weight:600;">{nowhp}</span><span style=" font-size:16pt;"> /{maxhp}</span></p></body></html>'
LV_FORMAT = u'<html><head/><body><p>Lv <span style=" font-size:16pt;">{lv}</span></p></body></html>'
COND_FORMAT= u"""<html><head/><body><p><span style=" font-size:16pt;"><span style=" color:{color};">■</span>{cond}</span><br/><span style=" font-size:10pt;">condition<span></p></body></html>"""

class ShipStatus(QWidget,Ui_Form):
    def __init__(self, parent=None):
        super(ShipStatus, self).__init__(parent)
        self.setupUi(self)

    def set_ship(self, ship):
        if ship is None:
            self.hide()
            return
        self.ship_name.setText(ship.name)
        self.ship_hp.setText(HP_FORMAT.format(nowhp=ship.nowhp, maxhp=ship.maxhp))
        self.hp_bar.setValue(float(ship.nowhp) / float(ship.maxhp) * 100)
        self.ship_lv.setText(LV_FORMAT.format(lv=ship.lv))
        self.ship_cond.setText(COND_FORMAT.format(color='#fde95f', cond=ship.cond))
        self.show()

if __name__ == '__main__':
    import sys

    con = sqlite3.connect('data.db', detect_types = sqlite3.PARSE_DECLTYPES)

    app = QApplication(sys.argv)

    st = DeckStatus(con)
    st.on_status_change()
    st.show()

    sys.exit(app.exec_())
