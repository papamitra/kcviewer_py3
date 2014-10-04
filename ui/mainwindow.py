# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QScrollArea, QSpacerItem, QSizePolicy)
from PyQt5.QtWebKitWidgets import QWebView
from PyQt5.QtCore import QFile, QSize

from ui.shipstatus import PortStatus
from ui.expedition import ExpeditionBox
import resource

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
        self.webView.setSizePolicy(QSizePolicy(QSizePolicy.Expanding,
                                               QSizePolicy.MinimumExpanding))
        self.webView.setMinimumSize(QSize(800, 600))

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
        self.expedition = ExpeditionBox(self)
        expdbox.addWidget(self.expedition)
        expdbox.addItem(QSpacerItem(40, 20,
                                    QSizePolicy.Minimum,
                                    QSizePolicy.Expanding))

        self.retranslateUi(MainWindow)
        #QtCore.QMetaObject.connectSlotsByName(MainWindow)

        file = QFile(':/ui/stylesheet.css')
        file.open(QFile.ReadOnly)
        stylesheet = unicode(file.readAll(), encoding='utf8')
        self.setStyleSheet(stylesheet)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("MainWindow", "KCViewer"))

