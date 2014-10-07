#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt5.QtCore import Qt, QUrl, QThread, pyqtSignal, QVariant
from PyQt5.QtWidgets import QApplication

import threading

import kcproxy
import kcviewer
import Queue
from kcsapi import KcsApi
import qtsignal

class ProxyThread(threading.Thread):
    #receive_msg = pyqtSignal(QVariant)

    def __init__(self, parent=None):
        super(ProxyThread, self).__init__(parent)
        self.proxy = kcproxy.KCProxy(on_receive = self.on_receive)

    def run(self):
        self.input_queue = Queue.Queue()
        self.api_thread = ApiThread(self.input_queue)
        self.api_thread.start()
        self.proxy.run()

    def on_receive(self, msg):
        api_msg = KcsApi.parse_respose(msg)
        if api_msg:
            self.input_queue.put(api_msg)

    def stop(self):
        self.proxy.shutdown()
        self.input_queue.put(None)
        self.api_thread.join()
        self.join()

class ApiThread(threading.Thread):
    def __init__(self, intput_queue):
        super(ApiThread, self).__init__()
        self.input_queue = intput_queue

    def run(self):
        global signal_emitter
        kcsapi = KcsApi()
        print('ApiThread start...')
        while True:
            d = self.input_queue.get()
            if d is None:
                break
            kcsapi.dispatch(d)
            signal_emitter.dispatch(d)

        print('ApiThread ...done')

def main():
    import sys

    if len(sys.argv) > 1:
        url = QUrl(sys.argv[1])
    else:
        url = QUrl(r'http://www.dmm.com/netgame/social/application/-/detail/=/app_id=854854/')

    app = QApplication(sys.argv)
    app.setApplicationName('kcviewer')

    global signal_emitter
    signal_emitter = qtsignal.Signal()

    proxythread = ProxyThread()
    proxythread.start()

    browser = kcviewer.KCView(proxythread.proxy.port(), url)

    # FIXME
    signal_emitter.api_port.connect(browser.status_page.portstatus.on_status_change)
    signal_emitter.api_port.connect(browser.status_page.expedition.on_status_change)

    #proxythread.receive_msg.connect(browser.on_receive)

    browser.show()

    ret = app.exec_()
    proxythread.stop()

    sys.exit(ret)

if __name__ == '__main__':
    main()
