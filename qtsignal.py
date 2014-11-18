# -*- coding: utf-8 -*-

from PyQt5.QtCore import pyqtSignal, QObject

class SignalEmitter(QObject):
    api_start2 = pyqtSignal()
    slot_item = pyqtSignal()
    api_port = pyqtSignal()
    def __init__(self):
        super(SignalEmitter, self).__init__()

    def dispatch(self, msg_type, path):
        if msg_type == 'response':
            if path == '/kcsapi/api_start2':
                self.api_start2.emit()
            elif path == '/kcsapi/api_port/port' or \
                 path == '/kcsapi/api_get_member/ship2':
                self.api_port.emit()
            elif path == '/kcsapi/api_get_member/slot_item':
                self.slot_item.emit()
        elif msg_type == 'request':
            if path == '/kcsapi/api_req_hensei/change' or \
               path == '/kcsapi/api_req_kaisou/slotset' or \
               path == '/kcsapi/api_req_kaisou/unsetslot_all' or \
               path == '/kcsapi/api_req_hokyu/charge':
                self.api_port.emit()
