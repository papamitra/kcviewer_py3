#!/usr/bin/env python2

from PyQt5.QtCore import Qt, QUrl, QSettings
from PyQt5.QtWidgets import (QAction, QApplication, QWidget)
from PyQt5.QtNetwork import QNetworkProxy
from PyQt5.QtWebKitWidgets import QWebView
from PyQt5 import QtWebKit, QtNetwork

from appdirs import AppDirs
import simplejson
import os

class KCView(QWidget):
    def __init__(self, url):
        super(QWidget, self).__init__()

        self.view = QWebView(self)
        self.view.load(url)
        self.view.show()

        self.app_dirs = AppDirs("kcviwer", "papamitra")

        # Load cookies
        user_data_dir = self.app_dirs.user_data_dir
        if not os.path.exists(user_data_dir):
            os.makedirs(user_data_dir)

        self.cookie_store = QSettings(user_data_dir + '/cookie', QSettings.NativeFormat)
        self.cookies = QtNetwork.QNetworkCookieJar()
        self.cookies.setAllCookies([QtNetwork.QNetworkCookie.parseCookies(c)[0] for c in self.get()])
        self.settings = QSettings(user_data_dir + '/config', QSettings.NativeFormat)

        self.view.page().networkAccessManager().setCookieJar(self.cookies)

        web_setting = QtWebKit.QWebSettings.globalSettings()
        web_setting.setAttribute(QtWebKit.QWebSettings.PluginsEnabled, True)
        web_setting.setAttribute(QtWebKit.QWebSettings.DnsPrefetchEnabled, True)
        web_setting.setAttribute(QtWebKit.QWebSettings.JavascriptEnabled, True)
        web_setting.setAttribute(QtWebKit.QWebSettings.OfflineStorageDatabaseEnabled, True)
        web_setting.setAttribute(QtWebKit.QWebSettings.LocalStorageEnabled, True)

    def put(self, value):
        key = 'cookieJar'
        self.cookie_store.setValue(key, simplejson.dumps(value))
        self.cookie_store.sync()

    def get(self):
        key = 'cookieJar'
        v = self.cookie_store.value(key, '{}')
        if v is None:
            return None
        return simplejson.loads(v)

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
