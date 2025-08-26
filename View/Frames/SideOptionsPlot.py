from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget, QLabel, QComboBox, QListWidget, QListWidgetItem, QCheckBox, QPushButton, QCalendarWidget, QVBoxLayout, QHBoxLayout, QScrollArea
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import psutil
from General.util import Util

class SideOptionsPlot(QWidget):
    def __init__(self, parent = None, language='en'):
        super().__init__(parent)
        self.language = language
        self.util = Util()
        self.font = QFont('Arial', 10)
        self.selected_dates = []

        self.btn_singleday_function = None
        self.btn_globaldays_function = None
        self.btn_manydays_function = None
        self.local_downloads_function = None

        self.init_ui()

    def init_ui(self):
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        container = QWidget()
        scroll.setWidget(container)
        self.layout = QVBoxLayout(container)

        lbl_drive = QLabel(self.util.dict_language[self.language]['lbl_dr'])
        lbl_drive.setFont(self.font)
        self.layout.addWidget(lbl_drive)

        self.combo_download_location = QComboBox()
        self.populate_combo_local()
        self.combo_download_location.currentIndexChanged.connect(self.change_local)
        self.layout.addWidget(self.combo_download_location)

        lbl_stations = QLabel(self.util.dict_language[self.language]['lbl_st'])
        lbl_stations.setFont(self.font)
        self.layout.addWidget(lbl_stations)

        self.list_all_stations = QListWidget()
        self.list_all_stations.setSelectionMode(QListWidget.MultiSelection)
        self.layout.addWidget(self.list_all_stations)

        btn_layout = QHBoxLayout()
        self.btn_select_all = QPushButton(self.util.dict_language[self.language]['btn_slt'])
        self.btn_select_all.clicked.connect(self.select_all_list)
        btn_layout.addWidget(self.btn_select_all)
        self.btn_clear_all = QPushButton(self.util.dict_language[self.language]['btn_clr'])
        self.btn_clear_all.clicked.connect(self.clear_all_list)
        btn_layout.addWidget(self.btn_clear_all)
        self.layout.addLayout(btn_layout)

        lbl_graph_opts = QLabel(self.util.dict_language[self.language]['lbl_plt'])
        self.layout.addWidget(lbl_graph_opts)

        self.checkbox_vars = {}
        for text in ['dH','H','dD','D','dZ','Z','dI','I','dF','F','dG','G','dX','X','dY','Y','Reference']:
            cb = QCheckBox(text)
            cb.stateChanged.connect(self.change_cal_state)
            self.layout.addWidget(cb)
            self.checkbox_vars[text] = cb

        self.cal_calm = QCalendarWidget()
        self.cal_calm.setDisabled(True)
        self.cal_calm.selectionChanged.connect(self.add_date)
        self.layout.addWidget(self.cal_calm)

        lbl_type_plot = QLabel(self.util.dict_language[self.language]['lbl_tpgraph'])
        self.layout.addWidget(lbl_type_plot)

        self.combo_type_plot = QComboBox()
        self.combo_type_plot.addItems([
            self.util.dict_language[self.language]['combo_sing'], 
            self.util.dict_language[self.language]['combo_sing_many'],
            self.util.dict_language[self.language]['combo_many'],
            self.util.dict_language[self.language]['combo_tide'],
            self.util.dict_language[self.language]['combo_difference']
        ])
        self.combo_type_plot.currentIndexChanged.connect(self.change_parameters)
        self.layout.addWidget(self.combo_type_plot)

        self.options_frame = QWidget()
        self.options_layout = QVBoxLayout()
        self.options_frame.setLayout(self.options_layout)
        self.layout.addWidget(self.options_frame)

    # ---------------- Funções ----------------
    def change_cal_state(self):
        enabled = any([self.checkbox_vars[key].isChecked() for key in ['dH','dD','dZ','dI','dF','dG','dX','dY','Reference']])
        self.cal_calm.setEnabled(enabled)

    def add_date(self):
        date = self.cal_calm.selectedDate().toPyDate()
        if date not in self.selected_dates:
            self.selected_dates.append(date)
        else:
            self.selected_dates.remove(date)

    def populate_list_options(self, stations):
        self.list_all_stations.clear()
        for s in stations:
            self.list_all_stations.addItem(QListWidgetItem(s))

    def populate_combo_local(self):
        self.combo_download_location.clear()
        combo_list = [p.device for p in psutil.disk_partitions()]
        self.combo_download_location.addItems(combo_list)

    def select_all_list(self):
        self.list_all_stations.selectAll()

    def clear_all_list(self):
        self.list_all_stations.clearSelection()

    def change_local(self, index):
        if self.local_downloads_function:
            self.local_downloads_function()

    def validate_number(self, number):
        try:
            float(number)
            return True
        except ValueError:
            return False

    def change_parameters(self, index):
        pass
