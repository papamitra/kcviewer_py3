#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt5.QtCore import Qt, QUrl, QThread, pyqtSignal, QVariant
from PyQt5.QtWidgets import QApplication

import threading

import kcproxy
import kcviewer
from kcsapi import KcsApiThread
import qtsignal

class ProxyThread(threading.Thread):

    def __init__(self, on_receive=None):
        super(ProxyThread, self).__init__()
        self.proxy = kcproxy.KCProxy(on_receive = on_receive)

    def run(self):
        self.proxy.run()

    def stop(self):
        self.proxy.shutdown()
        self.join()

def main():
    import sys

    if len(sys.argv) > 1:
        url = QUrl(sys.argv[1])
    else:
        url = QUrl(r'http://www.dmm.com/netgame/social/application/-/detail/=/app_id=854854/')

    app = QApplication(sys.argv)
    app.setApplicationName('kcviewer')

    signal_emitter = qtsignal.Signal()

    apithread = KcsApiThread(signal_emitter.dispatch)
    proxythread = ProxyThread(on_receive = apithread.request_dispatch)

    apithread.start()
    proxythread.start()

    browser = kcviewer.KCView(proxythread.proxy.port(), url)

    # FIXME
    signal_emitter.api_port.connect(browser.status_page.portstatus.on_status_change)
    signal_emitter.api_port.connect(browser.status_page.expedition.on_status_change)

    browser.show()

    ret = app.exec_()
    proxythread.stop()
    apithread.stop()

    sys.exit(ret)

if __name__ == '__main__':
    main()
