#!/usr/bin/env python2

from PyQt5.QtCore import Qt, QUrl, QSettings, QIODevice, QFile
from PyQt5.QtWidgets import (QAction, QApplication, QWidget)
from PyQt5.QtNetwork import QNetworkProxy, QNetworkAccessManager, QSslConfiguration, QSslCertificate, QSsl
from PyQt5.QtWebKitWidgets import QWebView
from PyQt5 import QtWebKit, QtNetwork

from appdirs import AppDirs
import simplejson
import os

class ProxyAccessManager(QNetworkAccessManager):
    def __init__(self,parent):
        super(ProxyAccessManager, self).__init__(parent)

        ssl_config = QSslConfiguration.defaultConfiguration()
        ssl_config.setProtocol(QSsl.SecureProtocols)

        certs = ssl_config.caCertificates()

        cert_file = QFile("/home/insight/.mitmproxy/mitmproxy-ca-cert.pem")
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


class KCView(QWidget):
    def __init__(self, url):
        super(KCView, self).__init__()

        self.app_dirs = AppDirs("kcviwer", "papamitra")

        self.view = QWebView(self)
        am = ProxyAccessManager(self)
        self.view.page().setNetworkAccessManager(am)

        """
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

        # Prepare cache dir
        cache_path = self.app_dirs.user_cache_dir

        local_storage_path = cache_path + '/LocalStorage'
        if not os.path.exists(local_storage_path):
            os.makedirs(local_storage_path)
        web_setting.setLocalStoragePath(local_storage_path)

        offlineStoragePath = cache_path + '/OfflineStorage'
        if not os.path.exists(offlineStoragePath):
            os.makedirs(offlineStoragePath)
        QtWebKit.QWebSettings.setOfflineStoragePath(offlineStoragePath)

        offlineWebApplicationCachePath = cache_path + '/OfflineWebApplication'
        if not os.path.exists(offlineWebApplicationCachePath):
            os.makedirs(offlineWebApplicationCachePath)
        QtWebKit.QWebSettings.setOfflineWebApplicationCachePath(offlineWebApplicationCachePath)
        """

        self.view.load(url)
        self.view.show()

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
