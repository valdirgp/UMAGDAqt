from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QComboBox, QPushButton, QCalendarWidget, QHBoxLayout
from PyQt5.QtCore import Qt
from General.util import Util
import psutil

class SideOptionsCalm(QWidget):
    def __init__(self, parent=None, language='en'):
        super().__init__(parent)
        self.lang = language
        self.util = Util()
        self.selected_calm_dates = []
        self.local_downloads_function = None

        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        self.combo_download_location = QComboBox()
        self.list_all_stations = QListWidget()
        self.startdate = QCalendarWidget()
        self.enddate = QCalendarWidget()
        self.cal_calm = QCalendarWidget()
        self.btn_clear_all = QPushButton()
        self.btn_plot_confirm = QPushButton()

        self.create_calm_plot_options()

    def create_calm_plot_options(self):
        # Drive selection
        self.layout.addWidget(QLabel(self.util.dict_language[self.lang]['lbl_dr']))
        self.populate_combo_local()
        self.combo_download_location.currentIndexChanged.connect(self.change_local)
        self.layout.addWidget(self.combo_download_location)

        # Station selection
        self.layout.addWidget(QLabel(self.util.dict_language[self.lang]['lbl_st']))
        self.layout.addWidget(self.list_all_stations)

        # Duration
        self.layout.addWidget(QLabel(self.util.dict_language[self.lang]['lbl_dur']))
        self.layout.addWidget(QLabel(self.util.dict_language[self.lang]['lbl_init_dt']))
        self.layout.addWidget(self.startdate)
        self.layout.addWidget(QLabel(self.util.dict_language[self.lang]['lbl_fin_dt']))
        self.layout.addWidget(self.enddate)

        # Calm date selection
        self.layout.addWidget(QLabel(self.util.dict_language[self.lang]['lbl_calm']))
        self.cal_calm.selectionChanged.connect(lambda: self.add_date(self.cal_calm, self.selected_calm_dates))
        self.layout.addWidget(self.cal_calm)

        # Buttons
        self.btn_clear_all.setText(self.util.dict_language[self.lang]['btn_clr'])
        self.btn_clear_all.clicked.connect(self.clean_all)
        self.layout.addWidget(self.btn_clear_all)

        self.btn_plot_confirm.setText(self.util.dict_language[self.lang]['btn_confirm'])
        self.layout.addWidget(self.btn_plot_confirm)

    def add_date(self, calendar_widget, list_type):
        date = calendar_widget.selectedDate().toPyDate()
        if date not in list_type:
            list_type.append(date)
        else:
            list_type.remove(date)

    def clean_all(self):
        self.selected_calm_dates.clear()

    def populate_list_options(self, list_widget, stations):
        list_widget.clear()
        for station in stations:
            list_widget.addItem(station)

    def populate_combo_local(self):
        combo_list = [part.device for part in psutil.disk_partitions()]
        self.combo_download_location.clear()
        self.combo_download_location.addItems(combo_list)

    def change_local(self):
        if self.local_downloads_function:
            self.local_downloads_function()
