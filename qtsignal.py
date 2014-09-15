
from PyQt5.QtCore import pyqtSignal, QObject

class Signal(QObject):
    api_start2 = pyqtSignal()
    slot_item = pyqtSignal()
    api_port = pyqtSignal()
    def __init__(self):
        super(Signal, self).__init__()

    def dispatch(self, msg):
        if msg.path == u'/kcsapi/api_start2':
            self.api_start2.emit()
        elif msg.path == u'/kcsapi/api_port/port':
            self.api_port.emit()
        elif msg.path == u'/kcsapi/api_get_member/slot_item':
            self.slot_item.emit()

