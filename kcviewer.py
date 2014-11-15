#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt5.QtCore import (Qt, QUrl, pyqtSlot, QSettings, QIODevice, QFile,
                          QMetaObject, QStandardPaths, QVariant, QDateTime)
from PyQt5.QtWidgets import (QAction, QApplication, QWidget, QMainWindow)
from PyQt5.QtNetwork import (QNetworkProxy, QNetworkProxyFactory, QNetworkAccessManager,
                             QSslConfiguration, QSslCertificate, QSsl,
                             QNetworkDiskCache, QNetworkCookieJar, QNetworkCookie)
from PyQt5.QtWebKitWidgets import QWebView
from PyQt5 import QtWebKit, QtNetwork
from PyQt5.QtGui import QDesktopServices

import simplejson
import os
import urlparse
from ui.mainwindow import MainWindow

class NetworkAccessManager(QNetworkAccessManager):
    def __init__(self, parent, on_request, on_response):
        super(NetworkAccessManager, self).__init__(parent)

        self.on_request = on_request
        self.on_response = on_response

        self.finished.connect(self.on_finished)

        proxy_url = os.environ.get('http_proxy')
        if proxy_url:
            url = urlparse.urlparse(proxy_url)
            proxy = QNetworkProxy()
            proxy.setType(QNetworkProxy.HttpProxy)
            proxy.setHostName(url.hostname)
            proxy.setPort(url.port)
            self.setProxy(proxy)

    def createRequest(self, op, req, outgoing_data = None):
        print("createRequest", req.url(), outgoing_data)
        return super(NetworkAccessManager, self).createRequest(op, req, outgoing_data)

    @pyqtSlot(object)
    def on_finished(self, reply):
        print(reply)

class CookieJar(QNetworkCookieJar):
    def __init__(self):
        super(CookieJar, self).__init__()

        cookie_location = os.path.join(QStandardPaths.writableLocation(QStandardPaths.DataLocation) ,'cookies.ini')
        self.cookie_store = QSettings(cookie_location, QSettings.IniFormat)
        self.load()

    def load(self):
        data = self.cookie_store.value('cookies', [])
        if data:
            self.setAllCookies([QNetworkCookie.parseCookies(c)[0] for c in data])

    def save(self):
        self.remove_expired_cookies()
        lines = []
        for cookie in self.allCookies():
            if not cookie.isSessionCookie():
                lines.append(cookie.toRawForm())
        self.cookie_store.setValue('cookies', QVariant(lines))

    def remove_expired_cookies(self):
        now = QDateTime.currentDateTime()
        cookies = [c for c in self.allCookies()
                   if c.isSessionCookie() or c.expirationDate() >= now]
        self.setAllCookies(cookies)

class KCView(MainWindow):
    def __init__(self, url, on_request, on_response):
        super(KCView, self).__init__()

        am = NetworkAccessManager(self, on_request, on_response)
        self.web_view.page().setNetworkAccessManager(am)

        disk_cache = QNetworkDiskCache()
        cache_location = QStandardPaths.writableLocation(QStandardPaths.CacheLocation)
        disk_cache.setCacheDirectory(cache_location)
        am.setCache(disk_cache)

        self.cookiejar = CookieJar()
        am.setCookieJar(self.cookiejar)

        web_setting = QtWebKit.QWebSettings.globalSettings()
        web_setting.setAttribute(QtWebKit.QWebSettings.PluginsEnabled, True)
        web_setting.setAttribute(QtWebKit.QWebSettings.JavascriptEnabled, True)

        self.web_view.load(url)
        self.web_view.show()

    def closeEvent(self, ev):
        self.cookiejar.save()
        super(KCView,self).closeEvent(ev)

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
