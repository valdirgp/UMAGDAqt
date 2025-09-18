from Model.Custom.CustomttkFrame import ScrollableFrame
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QListWidget, QAbstractItemView,
    QPushButton, QCalendarWidget, QDateEdit, QSizePolicy, QScrollBar
)
from PyQt5.QtCore import QDate
import psutil
from General.util import Util

class SideOptionsCalm(QWidget):
    def __init__(self, root, language):
        super().__init__(root)
        self.window = root
        self.lang = language
        self.util = Util()
        self.selected_calm_dates = []

        self.combo_local_download = None
        self.local_downloads_function = None

    # Creates options to create graphs
    def create_calm_plot_options(self):
        self.frame_side_functions_calm = ScrollableFrame(self.window, 255)
        self.frame_side_functions_calm.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.frame_side_functions_calm.setMinimumWidth(255)
        self.frame_side_functions_calm.setMaximumWidth(325)
        #self.frame_side_functions_calm.setFixedWidth(255)
        self.frame_side_functions_calm.setObjectName("sideOptionsCalmFrame")

        #layout = QVBoxLayout(self.frame_side_functions_calm.inner_frame)
        layout = self.frame_side_functions_calm.inner_layout
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(8)

        # Drive selection
        lbl_drive = QLabel(self.util.dict_language[self.lang]['lbl_dr'])
        layout.addWidget(lbl_drive)
        self.combo_download_location = QComboBox()
        self.populate_combo_local()
        self.combo_download_location.currentIndexChanged.connect(self.change_local)
        layout.addWidget(self.combo_download_location)

        # Station selection
        lbl_station = QLabel(self.util.dict_language[self.lang]['lbl_st'])
        layout.addWidget(lbl_station)
        self.list_all_stations = QListWidget()
        self.list_all_stations.setSelectionMode(QAbstractItemView.SingleSelection)
        layout.addWidget(self.list_all_stations)
        self.scrollbar = QScrollBar()
        self.list_all_stations.setVerticalScrollBar(self.scrollbar)

        # Duration label
        lbl_duration = QLabel(self.util.dict_language[self.lang]['lbl_dur'])
        layout.addWidget(lbl_duration)

        # Initial date
        lbl_initial_date = QLabel(self.util.dict_language[self.lang]['lbl_init_dt'])
        layout.addWidget(lbl_initial_date)
        self.startdate = QDateEdit()
        self.startdate.setDisplayFormat('dd/MM/yyyy')
        self.startdate.setCalendarPopup(True)
        self.startdate.setDate(QDate.currentDate())
        layout.addWidget(self.startdate)

        # Final date
        lbl_final_date = QLabel(self.util.dict_language[self.lang]['lbl_fin_dt'])
        layout.addWidget(lbl_final_date)
        self.enddate = QDateEdit()
        self.enddate.setDisplayFormat('dd/MM/yyyy')
        self.enddate.setCalendarPopup(True)
        self.enddate.setDate(QDate.currentDate())
        layout.addWidget(self.enddate)

        # Calm days calendar
        lbl_calm_date = QLabel(self.util.dict_language[self.lang]['lbl_calm'])
        layout.addWidget(lbl_calm_date)
        self.cal_calm = QCalendarWidget()
        self.cal_calm.setGridVisible(True)
        self.cal_calm.selectionChanged.connect(lambda: self.add_date(self.cal_calm, self.selected_calm_dates))
        self.cal_calm.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.cal_calm)

        # Clear all button
        self.btn_clear_all = QPushButton(self.util.dict_language[self.lang]['btn_clr'])
        self.btn_clear_all.clicked.connect(self.clean_all)
        layout.addWidget(self.btn_clear_all)

        # Confirm button
        self.btn_plot_confirm_H = QPushButton(self.util.dict_language[self.lang]['btn_confirm_H'])
        layout.addWidget(self.btn_plot_confirm_H)

        self.btn_plot_confirm_Z = QPushButton(self.util.dict_language[self.lang]['btn_confirm_Z'])
        layout.addWidget(self.btn_plot_confirm_Z)

        #self.frame_side_functions_calm.inner_frame.setLayout(layout)

        #self.frame_side_functions_calm.setLayout(QVBoxLayout())
        
        self.frame_side_functions_calm.show()

    # Add or remove selected date
    def add_date(self, calendar_widget, list_type):
        date = calendar_widget.selectedDate().toPyDate()
        if date not in list_type:
            list_type.append(date)
            # No direct equivalent to calevent_create in QCalendarWidget, so just store in list
        else:
            list_type.remove(date)
            # No direct equivalent to calevent_remove in QCalendarWidget

    # Clear all station's list
    def clean_all(self):
        self.selected_calm_dates.clear()
        # No direct equivalent to calevent_remove("all") in QCalendarWidget, so just clear the list

    # Fill a listbox with the given data
    def populate_list_options(self, listwidget, stations):
        listwidget.clear()
        for i in stations:
            listwidget.addItem(i)

    # Fill combobox that chooses path
    def populate_combo_local(self):
        combo_list = []
        particoes = psutil.disk_partitions()
        for particao in particoes:
            combo_list.append(particao.device)
        self.combo_download_location.clear()
        self.combo_download_location.addItems(combo_list)

    # Update all info came from the chosen drive 
    def change_local(self, index):
        if self.local_downloads_function:
            self.local_downloads_function()