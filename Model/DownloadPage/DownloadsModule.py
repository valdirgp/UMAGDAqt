from General.util import Util
from PyQt5.QtWidgets import QMessageBox, QProgressDialog
from dateutil.relativedelta import relativedelta
import time
import os

class DownloadModule():
    def __init__(self, language, root=None):
        self.util = Util()
        self.lang = language
        self.root = root  # QWidget principal para diálogos

    # verify if data archive isn't corrupted
    def is_string_readable_by_line(self, text):
        try:
            for i in range(len(text)):
                if '�' in text[i]: return False
            return True
        except UnicodeEncodeError:
            return False

    # format number of a month
    def format_month(self, month):
        match month:
            case 1:
                monthchar = 'jan'
            case 2:
                monthchar = 'feb'
            case 3:
                monthchar = 'mar'
            case 4:
                monthchar = 'apr'
            case 5:
                monthchar = 'may'
            case 6:
                monthchar = 'jun'
            case 7:
                monthchar = 'jul'
            case 8:
                monthchar = 'aug'
            case 9:
                monthchar = 'sep'
            case 10:
                monthchar = 'oct'
            case 11:
                monthchar = 'nov'
            case 12:
                monthchar = 'dec'
        return monthchar
    
    # Calculates the total number of downloads and the final date based in chosen duration
    def calculate_num_days(self, duration, duration_type, date):
        match duration_type:
            case 0:
                final_date = date + relativedelta(days=duration)
                num_days = final_date - date 
            case 1:
                final_date = date + relativedelta(months=duration)
                num_days = final_date - date
            case 2:
                final_date = date + relativedelta(years=duration)
                num_days = final_date - date
        return num_days.days, final_date
    
    # verify if all inputs has something selected
    def verify_inputs(self, selected_st, duration, duration_type):
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
    
    # creates pop view for progressbar with its especification
    def create_progressbar(self, progbar_dwd_type, total_downloads):
        self.total_downloads = total_downloads
        self.progbar_dwd_type = progbar_dwd_type
        self.porcentage = 0

        # Usando QProgressDialog para barra de progresso em PyQt5
        self.progress_dialog = QProgressDialog(
            self.util.dict_language[self.lang][self.progbar_dwd_type] + " 0%",
            None,
            0,
            100,
            self.root
        )
        self.progress_dialog.setWindowTitle("")
        self.progress_dialog.setWindowModality(True)
        self.progress_dialog.setMinimumWidth(300)
        self.progress_dialog.setValue(0)
        self.progress_dialog.setAutoClose(False)
        self.progress_dialog.setAutoReset(False)
        self.current_file = 1

    # updates progressbar and updating page
    def update_progressbar(self):
        try:
            self.porcentage = (self.current_file) * 100 / self.total_downloads
            self.current_file += 1
            self.progress_dialog.setValue(int(self.porcentage))
            self.progress_dialog.setLabelText(
                f"{self.util.dict_language[self.lang][self.progbar_dwd_type]} {self.progress_dialog.value():.1f}%"
            )
            if self.current_file == self.total_downloads + 1:
                time.sleep(1)
                self.progress_dialog.close()
        except Exception as error:
            print(error)

    # creates the path for downloading
    def create_dict_path(self, station, year, network):
        dir_path = os.path.join(self.lcl_download, 'Magnetometer')
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)

        dir_path = os.path.join(dir_path, network)
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)

        dir_path = os.path.join(dir_path, year)
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)

        dir_path = os.path.join(dir_path, station)
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)
        return dir_path