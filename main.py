#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt5.QtCore import Qt, QUrl, QThread, pyqtSignal, QVariant
from PyQt5.QtWidgets import QApplication

import threading

import kcproxy
import kcviewer
from kcsapi import KcsApiThread
import qtsignal

def main():
    import sys

    if len(sys.argv) > 1:
        url = QUrl(sys.argv[1])
    else:
        url = QUrl(r'http://www.dmm.com/netgame/social/application/-/detail/=/app_id=854854/')

    app = QApplication(sys.argv)
    app.setApplicationName('kcviewer')

    signal_emitter = qtsignal.SignalEmitter()

    apithread = KcsApiThread(signal_emitter.dispatch)
    apithread.start()

    browser = kcviewer.KCView(url, apithread)

    # FIXME
    signal_emitter.api_port.connect(browser.status_page.portstatus.on_status_change)
    signal_emitter.api_port.connect(browser.status_page.expedition.on_status_change)

    browser.show()

    ret = app.exec_()
    apithread.stop()

    sys.exit(ret)

if __name__ == '__main__':
    main()
