#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt5.QtCore import Qt, QUrl, QThread, pyqtSignal, QVariant
from PyQt5.QtWidgets import QApplication

import threading

import kcproxy
import kcviewer
import Queue

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
        #self.receive_msg.emit(msg)
        pass

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
        print('ApiThread start...')
        while True:
            d = self.input_queue.get()
            if d is None:
                break
        print('ApiThread ...done')

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

    #proxythread.receive_msg.connect(browser.on_receive)

    browser.show()

    ret = app.exec_()
    proxythread.stop()

    sys.exit(ret)
