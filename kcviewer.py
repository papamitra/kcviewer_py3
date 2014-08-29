#!/usr/bin/env python2

from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtWidgets import (QAction, QApplication, QWidget)
from PyQt5.QtNetwork import QNetworkProxy
from PyQt5.QtWebKitWidgets import QWebView

class KCView(QWidget):
    def __init__(self, url):
        super(QWidget, self).__init__()

        self.view = QWebView(self)
        self.view.load(url)
        self.view.show()


def main():
    import sys

    app = QApplication(sys.argv)

    if len(sys.argv) > 1:
        url = QUrl(sys.argv[1])
    else:
        url = QUrl('http://www.google.com/ncr')

    browser = KCView(url)
    browser.show()

    proxy = QNetworkProxy()
    proxy.setType(QNetworkProxy.HttpProxy);
    proxy.setHostName("127.0.0.1");
    proxy.setPort(8080);
    QNetworkProxy.setApplicationProxy(proxy);

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()    
