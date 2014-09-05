#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt5.QtCore import Qt, QUrl, QThread, pyqtSignal, QVariant
from PyQt5.QtWidgets import QApplication

import threading

import kcproxy
import kcviewer

class ProxyThread(QThread):
    receive_msg = pyqtSignal(QVariant)

    def __init__(self, parent=None):
        super(ProxyThread, self).__init__(parent)
        self.proxy = kcproxy.KCProxy(on_receive = self.on_receive)

    def run(self):
        self.proxy.run()

    def on_receive(self, msg):
        self.receive_msg.emit(msg)

    def stop(self):
        self.proxy.shutdown()
        self.wait()

if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        url = QUrl(sys.argv[1])
    else:
        url = QUrl('https://google.com/')

    app = QApplication(sys.argv)

    proxythread = ProxyThread()
    proxythread.start()

    browser = kcviewer.KCView(url)

    proxythread.receive_msg.connect(browser.on_receive)

    browser.show()

    ret = app.exec_()
    proxythread.stop()

    sys.exit(ret)
