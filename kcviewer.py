#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt5.QtCore import Qt, QUrl, pyqtSlot, QSettings, QIODevice, QFile, QMetaObject
from PyQt5.QtWidgets import (QAction, QApplication, QWidget, QMainWindow)
from PyQt5.QtNetwork import QNetworkProxy, QNetworkProxyFactory, QNetworkAccessManager, QSslConfiguration, QSslCertificate, QSsl
from PyQt5.QtWebKitWidgets import QWebView
from PyQt5 import QtWebKit, QtNetwork

import simplejson
import os
from mainwindow_ui import Ui_MainWindow

class ProxyAccessManager(QNetworkAccessManager):
    def __init__(self,parent):
        super(ProxyAccessManager, self).__init__(parent)

        ssl_config = QSslConfiguration.defaultConfiguration()
        ssl_config.setProtocol(QSsl.SecureProtocols)

        certs = ssl_config.caCertificates()

        cert_file = QFile("./cert/mitmproxy-ca-cert.pem")
        cert_file.open(QIODevice.ReadOnly)
        cert = QSslCertificate(cert_file)
        certs.append(cert)

        ssl_config.setCaCertificates(certs)
        QSslConfiguration.setDefaultConfiguration(ssl_config)

        print("NetworkAccessManager")
        proxy = QNetworkProxy()
        proxy.setType(QNetworkProxy.HttpProxy);
        proxy.setHostName("localhost");
        proxy.setPort(12345);
        #QNetworkProxy.setApplicationProxy(proxy);
        self.setProxy(proxy)

class KCView(QMainWindow, Ui_MainWindow):
    def __init__(self, url):
        super(KCView, self).__init__()
        self.setupUi(self)

        am = ProxyAccessManager(self)
        self.webView.page().setNetworkAccessManager(am)

        web_setting = QtWebKit.QWebSettings.globalSettings()
        web_setting.setAttribute(QtWebKit.QWebSettings.PluginsEnabled, True)
        #web_setting.setAttribute(QtWebKit.QWebSettings.DnsPrefetchEnabled, True)
        web_setting.setAttribute(QtWebKit.QWebSettings.JavascriptEnabled, True)
        #web_setting.setAttribute(QtWebKit.QWebSettings.LocalContentCanAccessRemoteUrls, True)
        #web_setting.setAttribute(QtWebKit.QWebSettings.OfflineStorageDatabaseEnabled, True)
        #web_setting.setAttribute(QtWebKit.QWebSettings.LocalStorageEnabled, True)

        self.webView.load(url)
        self.webView.show()

    def on_receive(self, msg):
        print('kcview:', msg)

def main():

    import sys

    if len(sys.argv) > 1:
        url = QUrl(sys.argv[1])
    else:
        url = QUrl('https://google.com/')

    app = QApplication(sys.argv)

    browser = KCView(url)
    browser.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
