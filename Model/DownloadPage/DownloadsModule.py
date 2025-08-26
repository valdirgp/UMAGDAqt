from General.util import Util
from dateutil.relativedelta import relativedelta
from PyQt5.QtWidgets import (
    QMessageBox, QDialog, QLabel, QProgressBar, QVBoxLayout
)
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
import time
import os


class DownloadModule:
    def __init__(self, language, parent=None):
        self.util = Util()
        self.lang = language
        self.parent = parent  # substitui root do Tkinter
        self.progress_window = None

    # verify if data archive isn't corrupted
    def is_string_readable_by_line(self, text):
        try:
            for i in range(len(text)):
                if '�' in text[i]:
                    return False
            return True
        except UnicodeEncodeError:
            return False

    # format number of a month
    def format_month(self, month):
        match month:
            case 1:
                return 'jan'
            case 2:
                return 'feb'
            case 3:
                return 'mar'
            case 4:
                return 'apr'
            case 5:
                return 'may'
            case 6:
                return 'jun'
            case 7:
                return 'jul'
            case 8:
                return 'aug'
            case 9:
                return 'sep'
            case 10:
                return 'oct'
            case 11:
                return 'nov'
            case 12:
                return 'dec'

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
                self.parent,
                self.util.dict_language[self.lang]["mgbox_error"],
                self.util.dict_language[self.lang]["mgbox_error_st"]
            )
            return False
        if duration == '':
            QMessageBox.information(
                self.parent,
                self.util.dict_language[self.lang]["mgbox_error"],
                self.util.dict_language[self.lang]["mgbox_error_dur"]
            )
            return False
        if duration_type == -1:
            QMessageBox.information(
                self.parent,
                self.util.dict_language[self.lang]["mgbox_error"],
                self.util.dict_language[self.lang]["mgbox_error_dur_type"]
            )
            return False
        return True

    # creates pop view for progressbar with its specification
    def create_progressbar(self, progbar_dwd_type, total_downloads):
        self.total_downloads = total_downloads
        self.progbar_dwd_type = progbar_dwd_type
        self.porcentage = 0
        self.current_file = 1

        self.progress_window = QDialog(self.parent)
        self.progress_window.setWindowTitle('')
        self.progress_window.setFixedSize(
            *map(int, self.util.dict_coord[self.progbar_dwd_type].split("x"))
        )

        layout = QVBoxLayout()

        self.progress_label = QLabel(
            f"{self.util.dict_language[self.lang][self.progbar_dwd_type]} 0%"
        )
        layout.addWidget(self.progress_label, alignment=Qt.AlignCenter)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        layout.addWidget(self.progress_bar)

        self.progress_window.setLayout(layout)
        self.progress_window.setModal(True)
        self.progress_window.show()
        QApplication.processEvents()

    # updates progressbar and updating page
    def update_progressbar(self):
        try:
            self.porcentage = (self.current_file) * 100 / self.total_downloads
            self.current_file += 1

            self.progress_bar.setValue(self.porcentage)
            self.progress_label.setText(
                f"{self.util.dict_language[self.lang][self.progbar_dwd_type]} {self.progress_bar.value():.1f}%"
            )

            if self.current_file == self.total_downloads + 1:
                time.sleep(1)
                self.progress_window.close()

            QApplication.processEvents()
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
