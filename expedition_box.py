# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QFrame,
                             QSizePolicy, QLabel, QPushButton, QSpacerItem)

import utils

MAX_FLEET_NUM = 4

class ExpeditionBox(QWidget):
    def __init__(self, parent=None):
        super(ExpeditionBox, self).__init__()
        
        self.vbox = QVBoxLayout()
        self.setLayout(self.vbox)
        self.label = QLabel()
        self.label.setText(u'遠征')
        self.vbox.addWidget(self.label)

        # horizontal line
        self.line = QFrame(self)
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)
        self.vbox.addWidget(self.line)

        #for i in range(1, MAX_FLEET_NUM):

if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)

    box = ExpeditionBox()
    box.show()

    ret = app.exec_()
    app = None
    sys.exit(ret)
