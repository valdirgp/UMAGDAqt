from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QComboBox, QLineEdit, QPushButton, QCalendarWidget, QHBoxLayout
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtCore import Qt
from General.util import Util
import psutil

class SideOptionsDownload(QWidget):
    def __init__(self, parent=None, language='en'):
        super().__init__(parent)
        self.util = Util()
        self.language = language

        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        # Widgets
        self.combo_download_location = QComboBox()
        self.list_all_stations = QListWidget()
        self.ent_durationchosen = QLineEdit()
        self.combo_durationtype = QComboBox()
        self.cal_initial_date = QCalendarWidget()
        self.btn_confirm = QPushButton()
        self.btn_readme = QPushButton()
        self.btn_select_all = QPushButton()
        self.btn_clear_all = QPushButton()

        self.create_download_options()

    def create_download_options(self):
        # Drive selection
        self.layout.addWidget(QLabel(self.util.dict_language[self.language]["lbl_dr"]))
        self.populate_combo_local()
        self.layout.addWidget(self.combo_download_location)

        # Station selection
        self.layout.addWidget(QLabel(self.util.dict_language[self.language]["lbl_st"]))
        self.list_all_stations.setSelectionMode(QListWidget.MultiSelection)
        self.layout.addWidget(self.list_all_stations)

        # Buttons for select/clear
        btn_layout = QHBoxLayout()
        self.btn_select_all.setText(self.util.dict_language[self.language]["btn_slt"])
        self.btn_select_all.clicked.connect(self.select_all_list)
        btn_layout.addWidget(self.btn_select_all)

        self.btn_clear_all.setText(self.util.dict_language[self.language]["btn_clr"])
        self.btn_clear_all.clicked.connect(self.clear_all_list)
        btn_layout.addWidget(self.btn_clear_all)

        self.layout.addLayout(btn_layout)

        # Duration
        self.layout.addWidget(QLabel(self.util.dict_language[self.language]["lbl_dur"]))
        self.ent_durationchosen.setValidator(QDoubleValidator())  # Apenas números
        self.layout.addWidget(self.ent_durationchosen)

        self.combo_durationtype.addItems([
            self.util.dict_language[self.language]["combo_day"],
            self.util.dict_language[self.language]["combo_month"],
            self.util.dict_language[self.language]["combo_year"]
        ])
        self.layout.addWidget(self.combo_durationtype)

        # Initial date
        self.layout.addWidget(QLabel(self.util.dict_language[self.language]["lbl_init_dt"]))
        self.layout.addWidget(self.cal_initial_date)

        # Confirm and Readme buttons
        self.btn_confirm.setText(self.util.dict_language[self.language]["btn_dwd"])
        self.layout.addWidget(self.btn_confirm)

        self.btn_readme.setText(self.util.dict_language[self.language]["btn_readme"])
        self.layout.addWidget(self.btn_readme)

    # Preenche lista de estações
    def populate_stations_listbox(self, stations):
        self.list_all_stations.clear()
        self.list_all_stations.addItems(stations)

    # Preenche combo de drives
    def populate_combo_local(self):
        drives = [d.device for d in psutil.disk_partitions()]
        self.combo_download_location.clear()
        self.combo_download_location.addItems(drives)

    # Seleciona todas as estações
    def select_all_list(self):
        for i in range(self.list_all_stations.count()):
            self.list_all_stations.item(i).setSelected(True)

    # Limpa todas as seleções
    def clear_all_list(self):
        for i in range(self.list_all_stations.count()):
            self.list_all_stations.item(i).setSelected(False)

    # Getters para integração com DownloadPage
    def get_local_download(self):
        return self.combo_download_location.currentText()

    def get_stations_selected(self):
        return [item.text() for item in self.list_all_stations.selectedItems()]

    def get_duration_chosen(self):
        return self.ent_durationchosen.text()

    def get_duration_type(self):
        return self.combo_durationtype.currentIndex()

    def get_date(self):
        return self.cal_initial_date.selectedDate().toPyDate()
