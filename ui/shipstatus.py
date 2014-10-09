#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3

from PyQt5.QtCore import pyqtSlot, pyqtSignal, QObject, QSize
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QSizePolicy, QLabel, QPushButton, QSpacerItem, QProgressBar,
                             QScrollArea, QStyleOption, QStyle)
from PyQt5.QtGui import QPixmap, QIcon, QColor, QPainter
import utils
import model
import slotitem

class DeckButton(QPushButton):

    def __init__(self, deck_no, parent):
        super(DeckButton, self).__init__(parent)
        self.parent = parent
        self.deck_no = deck_no
        self.setCheckable(True)
        if deck_no == 1:
            self.setChecked(True)
        else:
            self.setChecked(False)

    def nextCheckState(self):
        if not self.isChecked():
            self.setChecked(True)
            self.parent.on_deck_selected(self.deck_no)
            self.update()

    def checkStateSet(self):
        self.update()

    def update(self):
        con = self.parent.con
        deck = model.Port(con).deck(self.deck_no)
        self.setText('/' + deck.api_name)

class DeckSelector(QWidget):
    deck_selected = pyqtSignal(int)

    def __init__(self, con, parent):
        super(DeckSelector, self).__init__(parent)
        self.con = con
        self.decks = []
        self.deck_layout = QHBoxLayout()
        self.setLayout(self.deck_layout)
        #self.setStyleSheet(DECK_STYLESHEET)

        self.update()
        self.show()

    def on_deck_selected(self, deck_no):
        print("on_deck_Selected", deck_no)
        for deck in self.decks:
            if deck.deck_no != deck_no:
                deck.setChecked(False)
        self.deck_selected.emit(deck_no)

    def update(self):
        port = model.Port(self.con)
        decks_no = len(port.decks())
        for i in range(len(self.decks), decks_no):
            button = DeckButton(i+1, self)
            self.decks.append(button)
            self.deck_layout.addWidget(button)
            button.show()
        self.deck_layout.addItem(QSpacerItem(40, 20,
                                             QSizePolicy.Expanding,
                                             QSizePolicy.Minimum))

    # for apply stylesheet
    def paintEvent(self, pe):
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        s = self.style()
        s.drawPrimitive(QStyle.PE_Widget, opt, p, self)

class PortStatus(QWidget):
    def __init__(self, parent):
        super(PortStatus, self).__init__(parent)
        self.con = utils.connect_db()

        self.port = model.Port(self.con)

        self.vbox_layout = QVBoxLayout()
        self.vbox_layout.setSpacing(0)
        self.vbox_layout.setContentsMargins(10,0,10,0)

        self.setLayout(self.vbox_layout)

        self.ship_views = []
        self.now_deck = 1

        self.deckselector = DeckSelector(self.con, self)
        self.deckselector.deck_selected.connect(self.on_deck_selected)

        self.vbox_layout.addWidget(self.deckselector)
        self.deckselector.show()

        for _ in range(6):
            ui = ShipStatus(self)
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

    # for apply stylesheet
    def paintEvent(self, pe):
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        s = self.style()
        s.drawPrimitive(QStyle.PE_Widget, opt, p, self)

LV_FORMAT = u'<html><head/><body><p>Lv <span style=" font-size:16pt;">{lv}</span></p></body></html>'

#HP_FORMAT = u'<html><head/><body><p><span style=" font-size:16pt;">HP: </span><span style=" font-size:16pt; font-weight:600;">{0}</span><span style=" font-size:16pt;"> /{1}</span></p></body></html>'
HP_FORMAT = u'<html><head/><body><p>HP: <span style="font-weight:600;">{0}</span> /{1}</p></body></html>'

COND_FORMAT=u'<html><head/><body><p>{0}<br/><span style="font-size:8pt;">condition</span></p></body></html>'

class ShipHp(QWidget):
    def __init__(self, parent):
        super(ShipHp, self).__init__(parent)
        self.vbox = QVBoxLayout()
        self.vbox.setSpacing(0)
        self.vbox.setContentsMargins(0,3,0,3)

        self.setLayout(self.vbox)
        self.hp = QLabel(self)
        #self.hp.setMinimumSize(QSize(0, 50))
        self.vbox.addWidget(self.hp)

        self.hp_bar = QProgressBar(self)
        self.vbox.addWidget(self.hp_bar)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.hp_bar.setSizePolicy(sizePolicy)
        self.hp_bar.setMinimumSize(QSize(100, 10))
        self.hp_bar.setMaximumSize(QSize(100, 10))

        self.vbox.addItem(QSpacerItem(40, 20,
                                      QSizePolicy.Minimum,
                                      QSizePolicy.Expanding))

    def set_hp(self, hp, maxhp):
        self.hp.setText(HP_FORMAT.format(hp, maxhp))
        self.hp_bar.setValue(hp*100/maxhp)
        self.hp_bar.setFormat('')
        rate = float(hp) / float(maxhp)
        if rate <= 0.25:
            self.setProperty('damage', 'serious')
        elif rate <= 0.50:
            self.setProperty('damage', 'middle')
        elif rate <= 0.75:
            self.setProperty('damage', 'slight')
        else:
            self.setProperty('damage', 'none')

        self.style().unpolish(self.hp_bar)
        self.style().polish(self.hp_bar)
        self.update()

    # for apply stylesheet
    def paintEvent(self, pe):
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        s = self.style()
        s.drawPrimitive(QStyle.PE_Widget, opt, p, self)

class ShipCondition(QWidget):
    def __init__(self, parent):
        super(ShipCondition, self).__init__(parent)
        self.hbox = QHBoxLayout()
        self.hbox.setSpacing(3)
        self.hbox.setContentsMargins(0,0,0,10)

        self.setLayout(self.hbox)
        self.cond_signal = QWidget(self)
        self.cond_signal.setObjectName('condition_signal')
        self.cond_signal.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,
                                                   QSizePolicy.Fixed))
        self.cond_signal.setMinimumSize(QSize(20,20))
        self.cond_signal.setMaximumSize(QSize(20,20))
        self.hbox.addWidget(self.cond_signal)

        self.cond = QLabel(self)
        self.hbox.addWidget(self.cond)

        self.setProperty('condition', 'normal')

    def set_cond(self, cond):
        self.cond.setText(COND_FORMAT.format(str(cond)))
        if cond <= 20:
            self.setProperty('condition', 'serious tired')
        elif cond <= 29:
            self.setProperty('condition', 'middle tired')
        elif cond <= 39:
            self.setProperty('condition', 'slight tired')
        elif cond <= 49:
            self.setProperty('condition', 'normal')
        else:
            self.setProperty('condition', 'good')

        self.style().unpolish(self.cond_signal)
        self.style().polish(self.cond_signal)
        self.update()

    # for apply stylesheet
    def paintEvent(self, pe):
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        s = self.style()
        s.drawPrimitive(QStyle.PE_Widget, opt, p, self)

class ShipSlot(QWidget):
    sloticon_table = None
    type_table = {1: 'MainCanonLight',
                  2: 'MainCanonMedium',
                  3: 'MainCanonHeavy',
                  4: 'SecondaryCanon',
                  5: 'Torpedo',
                  6: 'Fighter',
                  7: 'DiveBomber',
                  8: 'TorpedoBomber',
                  9: 'ReconPlane',
                  10:'ReconSeaplane',
                  11:'Rader',
                  12:'AAshell',
                  13:'APShell',
                  14:'DamageControl',
                  15:'AAGun',
                  16:'HighAngleGun',
                  17:'ASW',
                  18:'Soner',
                  19:'EngineImprovement',
                  20:'LandingCraft',
                  21:'Autogyro',
                  22:'AntillerySpotter',
                  23:'AntiTorpedoBulge',
                  24:'SearchLight',
                  25:'DrumCanister',
                  26:'Facility',
                  27:'Flare',
                  28:'FleetCommandFacility',
                  29:'MaintenancePersonnel'}

    def __init__(self,parent):
        super(ShipSlot, self).__init__(parent)

        if self.sloticon_table is None:
            self.sloticon_table = slotitem.create_sloticontable()

        self.box = QHBoxLayout()
        self.box.setSpacing(3)
        self.box.setContentsMargins(0,5,0,5)

        self.setLayout(self.box)

    def set_slot(self, types):
        # remove all icon
        for i in reversed(range(self.box.count())):
            self.box.itemAt(i).widget().setParent(None)

        for t in types:
            type_name = self.type_table.get(t, 'unknown')
            if not type_name in self.sloticon_table:
                type_name = 'unknown'
            self.box.addWidget(slotitem.IconBox(self.sloticon_table[type_name]))

class ShipStatus(QWidget):
    def __init__(self, parent):
        super(ShipStatus, self).__init__(parent)
        self.con = parent.con

        self.hbox = QHBoxLayout()
        self.hbox.setContentsMargins(0,0,0,0)

        self.setLayout(self.hbox)

        self.name = QLabel(self)
        self.hbox.addWidget(self.name)
        self.name.setMinimumSize(QSize(80, 30))
        self.name.setMaximumSize(QSize(80, 30))


        self.lv = QLabel(self)
        self.hbox.addWidget(self.lv)
        self.lv.setMinimumSize(QSize(60, 30))
        self.lv.setMaximumSize(QSize(60, 30))

        self.hp = ShipHp(self)
        self.hbox.addWidget(self.hp)

        self.cond = ShipCondition(self)
        self.cond.setMinimumSize(QSize(80, 50))
        self.cond.setMaximumSize(QSize(80, 50))
        self.hbox.addWidget(self.cond)

        self.slot = ShipSlot(self)
        self.hbox.addWidget(self.slot)

        spacerItem = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.hbox.addItem(spacerItem)

        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        self.setSizePolicy(sizePolicy)
        self.setMinimumSize(QSize(500, 40))
        self.setMaximumSize(QSize(9999, 40))

    def set_ship(self, ship):
        if ship is None:
            self.hide()
            return
        self.name.setText(ship.name)
        self.hp.set_hp(ship.nowhp, ship.maxhp)
        self.lv.setText(LV_FORMAT.format(lv=ship.lv))
        self.cond.set_cond(cond=ship.cond)

        item_types = []
        for slot_id in ship.slot:
            print(slot_id)
            if slot_id == -1: continue
            slotitem = model.SlotItem(self.con, slot_id)
            print(slotitem)
            item_types.append(slotitem.item_type[3])
        self.slot.set_slot(item_types)

        self.show()

    # for apply stylesheet
    def paintEvent(self, pe):
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        s = self.style()
        s.drawPrimitive(QStyle.PE_Widget, opt, p, self)

if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)

    sc = QScrollArea()
    #sc.setStyleSheet(PORT_STYLESHEET)
    sc.setWidgetResizable(True)
    st = PortStatus()
    st.on_status_change()
    sc.setWidget(st)
    sc.show()

    ret = app.exec_()
    app = None
    sys.exit(ret)
