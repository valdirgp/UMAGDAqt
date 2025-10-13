from Model.Custom.CustomttkFrame import ScrollableFrame
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QListWidget, QAbstractItemView,
    QPushButton, QCalendarWidget, QDateEdit, QSizePolicy, QScrollBar, QLineEdit, QListWidgetItem
)
from PyQt5.QtCore import QDate, Qt
import psutil
from General.util import Util

class SideOptionsCalm(QWidget):
    def __init__(self, root, language, year, final, drive):
        super().__init__(root)
        self.window = root
        self.lang = language
        self.year = year
        self.final = final
        self.drive = drive
        self.util = Util()
        self.selected_calm_dates = []

        self.combo_local_download = None
        self.local_downloads_function = None

    # Função de filtro
    def filter_visible_items(self):
        filter_text = self.search_input.text().lower()
        for i in range(self.list_all_stations.count()):
            item = self.list_all_stations.item(i)
            item.setHidden(filter_text not in item.text().lower())

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

        # campo para digitar filtro
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Filtrar estações...")
        layout.addWidget(self.search_input)

        # Station selection
        lbl_station = QLabel(self.util.dict_language[self.lang]['lbl_st'])
        layout.addWidget(lbl_station)
        self.list_all_stations = QListWidget()
        self.list_all_stations.setSelectionMode(QAbstractItemView.SingleSelection)
        layout.addWidget(self.list_all_stations)
        self.scrollbar = QScrollBar()
        self.list_all_stations.setVerticalScrollBar(self.scrollbar)

        # Conectar filtro em tempo real
        self.search_input.textChanged.connect(self.filter_visible_items)

        # Duration label
        lbl_duration = QLabel(self.util.dict_language[self.lang]['lbl_dur'])
        layout.addWidget(lbl_duration)

        # Initial date
        lbl_initial_date = QLabel(self.util.dict_language[self.lang]['lbl_init_dt'])
        layout.addWidget(lbl_initial_date)
        self.startdate = QDateEdit()
        self.startdate.setDisplayFormat('dd/MM/yyyy')
        self.startdate.setCalendarPopup(True)
        hoje = QDate.currentDate()
        data = QDate(self.year[2], self.year[1], self.year[0])
        self.startdate.setDate(data)
        layout.addWidget(self.startdate)

        # Final date
        lbl_final_date = QLabel(self.util.dict_language[self.lang]['lbl_fin_dt'])
        layout.addWidget(lbl_final_date)
        self.enddate = QDateEdit()
        self.enddate.setDisplayFormat('dd/MM/yyyy')
        self.enddate.setCalendarPopup(True)
        hoje = QDate.currentDate()
        data = QDate(self.final[2], self.final[1], self.final[0])
        self.enddate.setDate(data)
        layout.addWidget(self.enddate)

        def sync_calendar_month_year(calendar, dateedit):
            # Pega o dia atualmente selecionado no calendário
            dia = calendar.selectedDate().day()
            # Cria uma nova data com o ano/mês do QDateEdit, mantendo o dia atual do calendário
            nova_data = QDate(dateedit.date().year(), dateedit.date().month(), dia)
            calendar.setSelectedDate(nova_data)

        # Calm days calendar
        lbl_calm_date = QLabel(self.util.dict_language[self.lang]['lbl_calm'])
        layout.addWidget(lbl_calm_date)
        self.cal_calm = QCalendarWidget()
        self.cal_calm.setGridVisible(True)
        hoje = QDate.currentDate()
        data = QDate(self.year[2], self.year[1], self.year[0])
        self.cal_calm.setSelectedDate(data)
        #self.add_date(self.cal_calm, self.selected_calm_dates)
        self.cal_calm.clicked.connect(lambda: self.add_date(self.cal_calm, self.selected_calm_dates))
        self.cal_calm.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Conecta ao dateChanged do QDateEdit
        self.startdate.dateChanged.connect(lambda new_date: sync_calendar_month_year(self.cal_calm, self.startdate))

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
        for st in stations:
            codigo = st.split()[0]   # pega só o código da estação (ex: "ARA")
            texto  = st              # texto completo (ex: "ARA (lat, lon, dip)")

            item = QListWidgetItem(texto)   # o que aparece na lista
            item.setData(Qt.UserRole, codigo)  # dado "oculto", só o código
            listwidget.addItem(item)
        self.filter_visible_items()

    # Fill combobox that chooses path
    def populate_combo_local(self):
        combo_list = []
        particoes = psutil.disk_partitions()
        for particao in particoes:
            combo_list.append(particao.device)
        self.combo_download_location.clear()
        self.combo_download_location.addItems(combo_list)

        index = self.combo_download_location.findText(self.drive)
        self.combo_download_location.setCurrentIndex(index)

    # Update all info came from the chosen drive 
    def change_local(self, index):
        if self.local_downloads_function:
            self.local_downloads_function()