from PyQt5.QtCore import QThread, pyqtSignal
import time

class DownloadThread(QThread):
    progress_signal = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.percent = 0
        self.running = True

    def run(self):
        while self.running:
            self.progress_signal.emit(self.percent)
            time.sleep(0.1)  # evita uso excessivo de CPU

    def update_progress(self, value):
        self.percent = value

    def stop(self):
        self.running = False
        self.quit()
        self.wait()
