'''from PyQt5.QtCore import QThread, pyqtSignal

class DownloadThread(QThread):
    progress_updated = pyqtSignal(int)  # % de progresso
    finished_download = pyqtSignal()    # sinal de fim de download

    def __init__(self, stations, duration, duration_type, date, download_module, embrace_obj=None, intermagnet_obj=None, options_frame=None, download_path=None):
        super().__init__()
        self.stations = stations
        self.duration = duration
        self.duration_type = duration_type
        self.date = date
        self.download_module = download_module
        self.embrace_obj = embrace_obj
        self.intermagnet_obj = intermagnet_obj
        self.options_frame = options_frame
        self.download_path = download_path

    def run(self):
        total = len(self.stations)
        for i, station in enumerate(self.stations, start=1):
            # Chama download genérico do DownloadModule
            self.download_module.download_station(
                station,
                self.duration,
                self.duration_type,
                self.date,
                embrace_obj=self.embrace_obj,
                intermagnet_obj=self.intermagnet_obj,
                options_frame=self.options_frame,
                download_path=self.download_path
            )
            percent = int((i / total) * 100)
            self.progress_updated.emit(percent)
        self.finished_download.emit()
'''


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
