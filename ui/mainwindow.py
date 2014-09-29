# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QScrollArea, QSpacerItem, QSizePolicy)
from PyQt5.QtWebKitWidgets import QWebView

from ui.shipstatus import PortStatus
from ui.expedition import ExpeditionBox

STYLESHEET = u"""
QWidget {
/* for debug
  border: 1px solid red;
  padding: 0px;
  margin-top: 0px;
  margin-bottom: 0px;
*/
}

* {
  font-family: "VL Gothic";
}

PortStatus{
  border: 2px solid darkgray;
  border-radius: 3px;
}

ShipStatus{
  border-bottom: 2px solid darkgray;
}

DeckButton {
  border: 0px;
  text-align: left;
  outline: none;
}

DeckButton:on {
  background-color: lightgray;
}

DeckSelector {
  border-bottom: 2px solid darkgray;
}

ExpeditionBox {
  border: 2px solid darkgray;
  border-radius: 3px;
}

/*
ExpeditionBox #hline {
  border: 2px solid darkgray;
}
*/

QProgressBar{
  border: 1px solid gray;
  border-radius: 2px;
}

QProgressBar::chunk{
  background-color: lightgreen;
  width: 10px;
}

QScrollArea {
  outline: none;
  border: none;
}
"""

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.setObjectName("MainWindow")
        self.resize(818, 618)
        font = QtGui.QFont()
        font.setFamily("Serif")
        font.setPointSize(10)
        self.setFont(font)
        self.centralWidget = QWidget(self)
        self.centralWidget.setObjectName("centralWidget")
        self.verticalLayout = QVBoxLayout(self.centralWidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.webView = QWebView(self.centralWidget)
        self.webView.setUrl(QtCore.QUrl("about:blank"))
        self.webView.setObjectName("webView")
        self.verticalLayout.addWidget(self.webView)
        self.setCentralWidget(self.centralWidget)

        hbox = QHBoxLayout()
        self.verticalLayout.addLayout(hbox)

        self.portstatus = PortStatus(self)

        sc = QScrollArea()
        sc.setWidgetResizable(True)
        sc.setWidget(self.portstatus)

        hbox.addWidget(sc)

        expdbox = QVBoxLayout()
        hbox.addLayout(expdbox)
        expedition = ExpeditionBox(self)
        expdbox.addWidget(expedition)
        expdbox.addItem(QSpacerItem(40, 20,
                                    QSizePolicy.Minimum,
                                    QSizePolicy.Expanding))

        self.retranslateUi(MainWindow)
        #QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.setStyleSheet(STYLESHEET)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("MainWindow", "KCViewer"))

