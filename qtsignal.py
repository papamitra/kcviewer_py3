
from PyQt5.QtCore import pyqtSignal, QObject

class SignalEmitter(QObject):
    api_start2 = pyqtSignal()
    slot_item = pyqtSignal()
    api_port = pyqtSignal()
    def __init__(self):
        super(SignalEmitter, self).__init__()

    def dispatch(self, path):
        if path == u'/kcsapi/api_start2':
            self.api_start2.emit()
        elif path == u'/kcsapi/api_port/port' or \
             path == u'/kcsapi/api_get_member/ship2':
            self.api_port.emit()
        elif path == u'/kcsapi/api_get_member/slot_item':
            self.slot_item.emit()

