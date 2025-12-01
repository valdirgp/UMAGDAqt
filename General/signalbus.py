from PyQt5.QtCore import QObject, pyqtSignal

class SignalBus(QObject):
    contorno_ready = pyqtSignal(object)

bus = SignalBus()