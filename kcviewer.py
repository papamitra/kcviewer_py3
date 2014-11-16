#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt5.QtCore import (Qt, QUrl, pyqtSlot, QSettings, QIODevice, QFile,
                          QMetaObject, QStandardPaths, QVariant, QDateTime)
from PyQt5.QtWidgets import (QAction, QApplication, QWidget, QMainWindow)
from PyQt5.QtNetwork import (QNetworkProxy, QNetworkProxyFactory, QNetworkAccessManager,
                             QSslConfiguration, QSslCertificate, QSsl,
                             QNetworkDiskCache, QNetworkCookieJar, QNetworkCookie, QNetworkRequest)
from PyQt5.QtWebKitWidgets import QWebView
from PyQt5 import QtWebKit, QtNetwork
from PyQt5.QtGui import QDesktopServices

import simplejson
import os
import urlparse
import re
from kcsapi import KcsCommand
from ui.mainwindow import MainWindow

class NetworkAccessManager(QNetworkAccessManager):
    def __init__(self, parent, apithread):
        super(NetworkAccessManager, self).__init__(parent)

        self.apithread = apithread

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
        try:
            path = req.url().path()
            print(path)

            content_type =  req.header(QNetworkRequest.ContentTypeHeader)
            if content_type == u'application/x-www-form-urlencoded':
                content = '' if outgoing_data is None else str(outgoing_data.peek(10*1000*1000))
                command = command = KcsCommand.command_table.get((KcsCommand.REQUEST, path), ApiReqUnknown)
                self.apithread.input_queue.push(command(path, content))
        except Exception, e:
            print(e)

        return super(NetworkAccessManager, self).createRequest(op, req, outgoing_data)

    @pyqtSlot(object)
    def on_finished(self, reply):
        try:
            path = reply.request().url().path()
            print('res path: ', path)

            content_type = reply.header(QNetworkRequest.ContentTypeHeader)
            print('res content_type: ', content_type)

            if content_type == u'application/json':
                content = '' if outgoing_data is None else str(outgoing_data.peek(10*1000*1000))
                command = KcsCommand.command_table.get((KcsCommand.RESPONSE, path), ApiResUnknown)
                self.apithread.input_queue.put(command(path, content))

            elif content_type == u'text/plain':
                content = '' if outgoing_data is None else str(outgoing_data.peek(10*1000*1000))
                if 0 == content.index("svdata="):
                    command = KcsCommand.command_table.get((KcsCommand.RESPONSE, path), ApiResUnknown)
                    self.apithread.input_queue.put(command(path, content[len("svdata="):]))

        except Exception, e:
                print(e)

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
    def __init__(self, url, apithread):
        super(KCView, self).__init__()

        am = NetworkAccessManager(self, apithread)
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
