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
import urllib.parse
import re
from kcsapi import KcsCommand
import command
from ui.mainwindow import MainWindow

class NetworkAccessManager(QNetworkAccessManager):
    def __init__(self, parent, apithread):
        super(NetworkAccessManager, self).__init__(parent)

        self.apithread = apithread

        proxy_url = os.environ.get('http_proxy')
        if proxy_url:
            url = urllib.parse.urlparse(proxy_url)
            proxy = QNetworkProxy()
            proxy.setType(QNetworkProxy.HttpProxy)
            proxy.setHostName(url.hostname)
            proxy.setPort(url.port)
            self.setProxy(proxy)

        self.reply_content = {}

    def createRequest(self, op, req, outgoing_data = None):
        try:
            path = req.url().path()
            content_type =  req.header(QNetworkRequest.ContentTypeHeader)
            if content_type == 'application/x-www-form-urlencoded':
                print(('req path: ', path))
                content = ''
                if outgoing_data is not None:
                    content = str(outgoing_data.peek(1024*1024), encoding='utf-8')

                self.apithread.input_queue.put(KcsCommand.create_req_command(path, content))
        except Exception as e:
            print(e)

        reply = super(NetworkAccessManager, self).createRequest(op, req, outgoing_data)
        self.reply_content[reply] = ''
        reply.readyRead.connect(self.on_ready_read)
        reply.finished.connect(self.on_finished)
        return reply

    def _get_content(self, reply):
        try:
            path = reply.request().url().path()
            content_type = reply.header(QNetworkRequest.ContentTypeHeader)

            if re.search('application/json', content_type) or \
               re.search('text/plain', content_type):
                content = str(reply.peek(reply.bytesAvailable()), encoding='utf-8')
                self.reply_content[reply] += content

        except Exception as e:
                print(e)

    @pyqtSlot()
    def on_ready_read(self):
        reply = self.sender()
        self._get_content(reply)

    @pyqtSlot()
    def on_finished(self):
        reply = self.sender()
        self._get_content(reply)

        try:
            path = reply.request().url().path()
            content_type = reply.header(QNetworkRequest.ContentTypeHeader)

            if re.search('application/json', content_type):
                print(('res path: ', path))
                content = self.reply_content[reply]
                self.apithread.input_queue.put(KcsCommand.create_res_command(path, content))

            elif re.search('text/plain', content_type):
                print(('res path: ', path))
                content = self.reply_content[reply][len("svdata="):]
                self.apithread.input_queue.put(KcsCommand.create_res_command(path, content))

        except Exception as e:
            print(e)

        del self.reply_content[reply]

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
