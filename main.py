#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtWidgets import QApplication

import threading

import kcproxy
import kcviewer

class ProxyThread(threading.Thread):
    def __init__(self):
        super(ProxyThread, self).__init__()
        self.proxy = kcproxy.KCProxy()

    def run(self):
        self.proxy.run()

    def stop(self):
        self.proxy.shutdown()
        self.join()

def closed():
    print("closed")

if __name__ == '__main__':
    proxythread = ProxyThread()
    proxythread.start()

    import sys

    if len(sys.argv) > 1:
        url = QUrl(sys.argv[1])
    else:
        url = QUrl('https://google.com/')

    app = QApplication(sys.argv)

    browser = kcviewer.KCView(url)
    browser.show()

    ret = app.exec_()
    proxythread.stop()

    sys.exit(ret)
