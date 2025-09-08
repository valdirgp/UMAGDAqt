from Model.Custom.CustomttkFrame import ScrollableFrame
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QListWidget, QAbstractItemView,
    QPushButton, QDateEdit, QSizePolicy, QScrollBar, QLineEdit
)
from PyQt5.QtCore import QDate
from PyQt5.QtGui import QIntValidator
import psutil
from General.util import Util

class SideOptionsDownload(QWidget):
    def __init__(self, root, language):
        super().__init__(root)
        self.language = language
        self.util = Util()
        #self.page_frame = root
        self.options_frame = None

    # create download widget
    def create_download_options(self):
        # Parent do ScrollableFrame agora é self, e não DownloadPage
        #self.options_frame = ScrollableFrame(self.page_frame, 255)
        #self.options_frame = ScrollableFrame(self, 255)
        #self.options_frame.setStyleSheet("background-color: #2c2c2c;")

        self.options_frame = ScrollableFrame(self, 255)
        layout = self.options_frame.inner_layout  # pega o layout do scroll
        layout.setContentsMargins(5,5,5,5)
        layout.setSpacing(8)



        # Drive selection
        lbl_drive = QLabel(self.util.dict_language[self.language]["lbl_dr"])
        layout.addWidget(lbl_drive)
        self.combo_download_location = QComboBox()
        self.populate_combo_local()
        layout.addWidget(self.combo_download_location)

        # Station selection
        lbl_station = QLabel(self.util.dict_language[self.language]["lbl_st"])
        layout.addWidget(lbl_station)
        self.list_all_stations = QListWidget()
        self.list_all_stations.setSelectionMode(QAbstractItemView.MultiSelection)
        layout.addWidget(self.list_all_stations)
        self.scrollbar = QScrollBar()
        self.list_all_stations.setVerticalScrollBar(self.scrollbar)

        # Select/Clear all buttons
        btns_layout = QHBoxLayout()
        self.btn_select_all = QPushButton(self.util.dict_language[self.language]["btn_slt"])
        self.btn_select_all.clicked.connect(self.select_all_list)
        btns_layout.addWidget(self.btn_select_all)
        self.btn_clear_all = QPushButton(self.util.dict_language[self.language]["btn_clr"])
        self.btn_clear_all.clicked.connect(self.clear_all_list)
        btns_layout.addWidget(self.btn_clear_all)
        layout.addLayout(btns_layout)

        # Duration
        lbl_duration = QLabel(self.util.dict_language[self.language]["lbl_dur"])
        layout.addWidget(lbl_duration)
        duration_layout = QHBoxLayout()
        self.ent_durationchosen = QLineEdit()
        self.ent_durationchosen.setPlaceholderText("1")
        self.ent_durationchosen.setFixedWidth(60)
        # Adicionando validador para aceitar apenas números inteiros
        self.ent_durationchosen.setValidator(QIntValidator(1, 9999, self.ent_durationchosen))
        duration_layout.addWidget(self.ent_durationchosen)
        self.combo_durationtype = QComboBox()
        self.combo_durationtype.addItems([
            self.util.dict_language[self.language]["combo_day"],
            self.util.dict_language[self.language]["combo_month"],
            self.util.dict_language[self.language]["combo_year"]
        ])
        duration_layout.addWidget(self.combo_durationtype)
        layout.addLayout(duration_layout)

        # Initial date
        lbl_initial_date = QLabel(self.util.dict_language[self.language]["lbl_init_dt"])
        layout.addWidget(lbl_initial_date)
        self.cal_initial_date = QDateEdit()
        self.cal_initial_date.setDisplayFormat('dd/MM/yyyy')
        self.cal_initial_date.setCalendarPopup(True)
        self.cal_initial_date.setDate(QDate.currentDate())
        layout.addWidget(self.cal_initial_date)

        # Confirm Download button
        self.btn_confirm = QPushButton(self.util.dict_language[self.language]["btn_dwd"])
        layout.addWidget(self.btn_confirm)

        # Readme button
        self.btn_readme = QPushButton(self.util.dict_language[self.language]["btn_readme"])
        layout.addWidget(self.btn_readme)

        #self.options_frame.inner_frame.setLayout(layout)
        #self.options_frame.setLayout(QVBoxLayout())
        self.options_frame.show()

    # fill all listbox
    def populate_stations_listbox(self, listwidget, stations):
        listwidget.clear()
        for i in stations:
            listwidget.addItem(i)

    # fill combox with all drive options
    def populate_combo_local(self):
        combo_list = []
        all_drives = psutil.disk_partitions()
        for drive in all_drives:
            combo_list.append(drive.device)
        self.combo_download_location.clear()
        self.combo_download_location.addItems(combo_list)
        if combo_list:
            self.combo_download_location.setCurrentIndex(0)

    # select all station's list
    def select_all_list(self):
        self.list_all_stations.selectAll()

    # clear all station's list
    def clear_all_list(self):
        self.list_all_stations.clearSelection()