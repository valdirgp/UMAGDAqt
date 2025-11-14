from General.util import Util
from PyQt5.QtWidgets import QProgressDialog
import os
import threading
from PyQt5.QtCore import pyqtSignal, QObject

class DownloadModule(QObject):
    #progress_signal = pyqtSignal()  # sem argumentos, cada arquivo concluído
    progress_signal = pyqtSignal(str, object)  # agora envia mensagem
    def __init__(self, language, root=None):
        super().__init__()
        self.util = Util()
        self.lang = language
        self.root = root  # parent QWidget para diálogos
        self._lock = threading.Lock() #NEW

        self.progress_signal.connect(self.update_progressbar)  # conecta sinal

    def is_string_readable_by_line(self, text):
        try:
            for i in range(len(text)):
                if '�' in text[i]:
                    return False
            return True
        except UnicodeEncodeError:
            return False

    def format_month(self, month):
        match month:
            case 1: return 'jan'
            case 2: return 'feb'
            case 3: return 'mar'
            case 4: return 'apr'
            case 5: return 'may'
            case 6: return 'jun'
            case 7: return 'jul'
            case 8: return 'aug'
            case 9: return 'sep'
            case 10: return 'oct'
            case 11: return 'nov'
            case 12: return 'dec'

    def calculate_num_days(self, duration, duration_type, date):
        from dateutil.relativedelta import relativedelta
        match duration_type:
            case 0:
                final_date = date + relativedelta(days=duration)
            case 1:
                final_date = date + relativedelta(months=duration)
            case 2:
                final_date = date + relativedelta(years=duration)
        num_days = (final_date - date).days
        return num_days, final_date

    def verify_inputs(self, selected_st, duration, duration_type):
        from PyQt5.QtWidgets import QMessageBox
        if selected_st == []:
            QMessageBox.information(
                self.root,
                self.util.dict_language[self.lang]["mgbox_error"],
                self.util.dict_language[self.lang]["mgbox_error_st"]
            )
            return False
        if duration == '':
            QMessageBox.information(
                self.root,
                self.util.dict_language[self.lang]["mgbox_error"],
                self.util.dict_language[self.lang]["mgbox_error_dur"]
            )
            return False
        if duration_type == -1:
            QMessageBox.information(
                self.root,
                self.util.dict_language[self.lang]["mgbox_error"],
                self.util.dict_language[self.lang]["mgbox_error_dur_type"]
            )
            return False
        return True

    
    def create_progressbar(self, progbar_dwd_type, total_downloads):
        self.total_downloads = max(1, int(total_downloads))
        self.progbar_dwd_type = progbar_dwd_type
        self.current_file = 0
        self.progress_dialog = QProgressDialog(
            self.util.dict_language[self.lang][progbar_dwd_type] + " 0%",
            None,
            0,
            100,
            self.root
        )
        self.progress_dialog.setMinimumWidth(300)
        self.progress_dialog.setValue(0)
        self.progress_dialog.show()


    def update_progressbar(self, message="", responses=[]):
        if not hasattr(self, "progress_dialog"):
            return
        with self._lock:
            self.current_file += 1
            percent = int(self.current_file * 100 / self.total_downloads)
            self.progress_dialog.setValue(percent)

            base_text = self.util.dict_language[self.lang][self.progbar_dwd_type]
            if message:
                # mostra nome do arquivo + status dentro da barra
                self.progress_dialog.setLabelText(f"{base_text} {percent}%\n{message}")
            else:
                self.progress_dialog.setLabelText(f"{base_text} {percent}%")

            if self.current_file >= self.total_downloads:
                self.progress_dialog.close()
                from PyQt5.QtWidgets import QMessageBox
                title = self.util.dict_language[self.lang]["mgbox_success"]
                text = "\n".join(responses) if len(responses) > 1 else "Download concluído."

                QMessageBox.information(None, title, text)

    def create_dict_path(self, station, year, network):
        dir_path = os.path.join(self.lcl_download, 'Magnetometer', network, year, station)
        os.makedirs(dir_path, exist_ok=True)
        return dir_path

    def download_station(self, station, duration, duration_type, date, embrace_obj=None, intermagnet_obj=None, options_frame=None, download_path=None):
        """
        Faz download de uma estação chamando Embrace ou Intermagnet
        """
        self.lcl_download = download_path
        if embrace_obj and station in embrace_obj.create_stationlist():
            embrace_obj.initialize_download_Embrace(
                options_frame,
                download_path,
                [station],
                duration,
                duration_type,
                date
            )
        if intermagnet_obj and station in intermagnet_obj.create_stationlist():
            intermagnet_obj.initialize_download_Intermagnet(
                options_frame,
                download_path,
                [station],
                duration,
                duration_type,
                date
            )
