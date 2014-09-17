#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3

from ship_status import Ui_Form
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QObject, QSize
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QSizePolicy, QLabel, QPushButton, QSpacerItem)
import utils
import model

DECK_STYLESHEET = u"""
QPushButton{
    border: 0px;
}
"""

class DeckButton(QPushButton):

    def __init__(self, deck_no, parent):
        super(DeckButton, self).__init__(parent)
        self.parent = parent
        self.deck_no = deck_no
        self.setCheckable(True)

    def nextCheckState(self):
        if not self.isChecked():
            self.setChecked(True)
            self.parent.on_deck_selected(self.deck_no)

class DeckSelector(QWidget):
    deck_selected = pyqtSignal(int)

    def __init__(self, con, parent):
        super(DeckSelector, self).__init__(parent)
        self.con = con
        self.decks = []
        self.deck_layout = QHBoxLayout()
        self.setLayout(self.deck_layout)
#        self.setStyleSheet(DECK_STYLESHEET)

        for i in range(1,5):
            button = DeckButton(i, self)
            button.setText("test")
            self.decks.append(button)
            self.deck_layout.addWidget(button)
            button.show()

        self.show()

    def on_deck_selected(self, deck_no):
        print("on_deck_Selected", deck_no)
        for deck in self.decks:
            if deck.deck_no != deck_no:
                deck.setChecked(False)
        self.deck_selected.emit(deck_no)

class PortStatus(QWidget):
    def __init__(self):
        super(PortStatus, self).__init__()
        self.con = utils.connect_db()

        self.port = model.Port(self.con)

        self.vbox_layout = QVBoxLayout()
        self.setLayout(self.vbox_layout)

        self.ship_views = []
        self.now_deck = 1

        sizePolicy = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        self.setSizePolicy(sizePolicy)
        self.setMinimumSize(QSize(500, 0))
        self.setMaximumSize(QSize(800, 16777215))

        self.deckselector = DeckSelector(self.con, self)
        self.deckselector.deck_selected.connect(self.on_deck_selected)

        self.vbox_layout.addWidget(self.deckselector)
        self.deckselector.show()

        for _ in range(6):
            ui = ShipStatus()
            self.ship_views.append(ui)
            self.vbox_layout.addWidget(ui)
            ui.hide()

        self.vbox_layout.addItem(QSpacerItem(40, 20,
                                             QSizePolicy.Minimum,
                                             QSizePolicy.Expanding))

    @pyqtSlot()
    def on_status_change(self):
        print("on_status_change")
        deck = self.port.deck(self.now_deck)
        for (i,ship) in enumerate(deck.ships()):
            ui = self.ship_views[i]
            ui.set_ship(ship)

    @pyqtSlot(int)
    def on_deck_selected(self, deck_no):
        self.now_deck = deck_no
        self.on_status_change()

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
    st = PortStatus()
    emitter.sig.connect(st.on_status_change)
    st.show()

    emitter.sig.emit()
    sys.exit(app.exec_())
