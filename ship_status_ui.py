#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3

from ship_status import Ui_Form
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QObject, QSize
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QSizePolicy, QLabel
import utils
import model

class DeckStatus(QWidget):
    def __init__(self):
        super(DeckStatus, self).__init__()
        self.con = utils.connect_db()

        self.vbox_layout = QVBoxLayout()
        self.setLayout(self.vbox_layout)
        self.deck_layout = QHBoxLayout()

        self.ship_views = []
        self.deck_labels = []

        self.now_deck = 1

        sizePolicy = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        self.setSizePolicy(sizePolicy)
        self.setMinimumSize(QSize(500, 0))
        self.setMaximumSize(QSize(800, 16777215))

        for _ in range(4):
            ui = QLabel()
            self.deck_labels.append(ui)

        for _ in range(6):
            ui = ShipStatus()
            self.ship_views.append(ui)
            self.vbox_layout.addWidget(ui)
            ui.hide()

    @pyqtSlot()
    def on_status_change(self):
        print("on_status_change")
        deck = model.DeckPortInfo(self.con, self.now_deck)
        for (i,ship) in enumerate(deck.ships()):
            ui = self.ship_views[i]
            ui.set_ship(ship)

    def closeEvent(self, event):
        print("close event");
        self.con.close()
        event.accept()

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

    class Emitter(QObject):
        sig = pyqtSignal()
        def __init__(self):
            super(Emitter, self).__init__()

    app = QApplication(sys.argv)

    emitter = Emitter()
    st = DeckStatus()
    emitter.sig.connect(st.on_status_change)
    st.show()

    emitter.sig.emit()
    sys.exit(app.exec_())
