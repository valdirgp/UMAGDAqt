from PyQt5.QtCore import QThread, pyqtSignal

class InitThread(QThread):
    finished = pyqtSignal(bool)

    def __init__(self, main_control):
        super().__init__()
        self.main_control = main_control

    def run(self):
        ok = self.main_control.initialize_app()
        self.finished.emit(ok)