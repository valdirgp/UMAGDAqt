from Model.Custom.CustomttkFrame import ScrollableFrame
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QListWidget, QAbstractItemView,
    QPushButton, QCheckBox, QDateEdit, QSizePolicy, QScrollBar, QFrame
)
from PyQt5.QtCore import QDate
import psutil
from General.util import Util

class SideOptionsPlot(QWidget):
    def __init__(self, root, language):
        super().__init__(root)
        self.util = Util()
        self.window = root
        self.language = language
        self.selected_dates = []

        self.btn_singleday_function = None
        self.btn_globaldays_function = None
        self.btn_manydays_function = None
        self.local_downloads_function = None

    # creates options to create graphs
    def create_plot_options(self):
        self.frame_side_functions = ScrollableFrame(self.window, 255)
        self.frame_side_functions.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.frame_side_functions.setMinimumWidth(255)
        self.frame_side_functions.setMaximumWidth(255)
        self.frame_side_functions.setFixedWidth(255)
        self.frame_side_functions.setObjectName("sideOptionsPlotFrame")

        layout = QVBoxLayout(self.frame_side_functions.inner_frame)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(8)

        # Drive selection
        lbl_drive = QLabel(self.util.dict_language[self.language]['lbl_dr'])
        layout.addWidget(lbl_drive)
        self.combo_download_location = QComboBox()
        self.populate_combo_local()
        self.combo_download_location.currentIndexChanged.connect(self.change_local)
        layout.addWidget(self.combo_download_location)

        # Station selection
        lbl_station = QLabel(self.util.dict_language[self.language]['lbl_st'])
        layout.addWidget(lbl_station)
        self.list_all_stations = QListWidget()
        self.list_all_stations.setSelectionMode(QAbstractItemView.MultiSelection)
        layout.addWidget(self.list_all_stations)
        self.scrollbar = QScrollBar()
        self.list_all_stations.setVerticalScrollBar(self.scrollbar)

        # Select/Clear all buttons
        btns_layout = QHBoxLayout()
        self.btn_select_all = QPushButton(self.util.dict_language[self.language]['btn_slt'])
        self.btn_select_all.clicked.connect(self.select_all_list)
        btns_layout.addWidget(self.btn_select_all)
        self.btn_clear_all = QPushButton(self.util.dict_language[self.language]['btn_clr'])
        self.btn_clear_all.clicked.connect(self.clear_all_list)
        btns_layout.addWidget(self.btn_clear_all)
        layout.addLayout(btns_layout)

        # Plot options
        lbl_plot_opts = QLabel(self.util.dict_language[self.language]['lbl_plt'])
        layout.addWidget(lbl_plot_opts)

        # Plot type checkboxes
        self.checkboxes = {}
        plot_types = [
            ('dH', 'is_dH'), ('H', 'is_H'),
            ('dD', 'is_dD'), ('D', 'is_D'),
            ('dZ', 'is_dZ'), ('Z', 'is_Z'),
            ('dI', 'is_dI'), ('I', 'is_I'),
            ('dF', 'is_dF'), ('F', 'is_F'),
            ('dG', 'is_dG'), ('G', 'is_G'),
            ('dX', 'is_dX'), ('X', 'is_X'),
            ('dY', 'is_dY'), ('Y', 'is_Y'),
            ('Reference', 'is_reference')
        ]
        for i in range(0, len(plot_types), 2):
            row_layout = QHBoxLayout()
            for j in range(2):
                if i + j < len(plot_types):
                    label, attr = plot_types[i + j]
                    cb = QCheckBox(label)
                    setattr(self, attr, cb)
                    row_layout.addWidget(cb)
            layout.addLayout(row_layout)

        # Graph options
        lbl_graph_opts = QLabel(self.util.dict_language[self.language]['lbl_graph_opts'])
        layout.addWidget(lbl_graph_opts)
        row_opts = QHBoxLayout()
        self.is_bold_text = QCheckBox(self.util.dict_language[self.language]['check_bold'])
        row_opts.addWidget(self.is_bold_text)
        self.is_grid_graph = QCheckBox(self.util.dict_language[self.language]['check_grid'])
        row_opts.addWidget(self.is_grid_graph)
        layout.addLayout(row_opts)

        # Graph type selection
        lbl_tpgraph = QLabel(self.util.dict_language[self.language]['lbl_tpgraph'])
        layout.addWidget(lbl_tpgraph)
        self.combo_type_plot = QComboBox()
        self.combo_type_plot.addItems([
            self.util.dict_language[self.language]['combo_sing'],
            self.util.dict_language[self.language]['combo_sing_many'],
            self.util.dict_language[self.language]['combo_many'],
            self.util.dict_language[self.language]['combo_tide'],
            self.util.dict_language[self.language]['combo_difference']
        ])
        self.combo_type_plot.currentIndexChanged.connect(self.change_parameters)
        layout.addWidget(self.combo_type_plot)

        # Placeholder for dynamic options
        self.options_frame = QFrame()
        self.options_layout = QVBoxLayout(self.options_frame)
        self.options_frame.setLayout(self.options_layout)
        layout.addWidget(self.options_frame)

        # Calm days calendar
        lbl_calm = QLabel(self.util.dict_language[self.language]['lbl_calm'])
        layout.addWidget(lbl_calm)
        self.cal_calm = QDateEdit()
        self.cal_calm.setDisplayFormat('dd/MM/yyyy')
        self.cal_calm.setCalendarPopup(True)
        self.cal_calm.setDate(QDate.currentDate())
        layout.addWidget(self.cal_calm)

        self.frame_side_functions.inner_frame.setLayout(layout)
        self.frame_side_functions.setLayout(QVBoxLayout())
        self.frame_side_functions.show()

    # create a child for frame_side_functions to have one day options
    def create_oneday_options(self):
        self.clear_options_frame()
        lbl_date = QLabel(self.util.dict_language[self.language]['lbl_dt'])
        self.options_layout.addWidget(lbl_date)
        self.date = QDateEdit()
        self.date.setDisplayFormat('dd/MM/yyyy')
        self.date.setCalendarPopup(True)
        self.date.setDate(QDate.currentDate())
        self.options_layout.addWidget(self.date)
        self.btn_singleday_confirm = QPushButton(self.util.dict_language[self.language]['btn_confirm'])
        if self.btn_singleday_function:
            self.btn_singleday_confirm.clicked.connect(self.btn_singleday_function)
        self.options_layout.addWidget(self.btn_singleday_confirm)

    # create a child for frame_side_functions to have many days options
    def create_manydays_options(self):
        self.clear_options_frame()
        lbl_initial_date = QLabel(self.util.dict_language[self.language]['lbl_init_dt'])
        self.options_layout.addWidget(lbl_initial_date)
        self.startdate = QDateEdit()
        self.startdate.setDisplayFormat('dd/MM/yyyy')
        self.startdate.setCalendarPopup(True)
        self.startdate.setDate(QDate.currentDate())
        self.options_layout.addWidget(self.startdate)

        lbl_final_date = QLabel(self.util.dict_language[self.language]['lbl_fin_dt'])
        self.options_layout.addWidget(lbl_final_date)
        self.enddate = QDateEdit()
        self.enddate.setDisplayFormat('dd/MM/yyyy')
        self.enddate.setCalendarPopup(True)
        self.enddate.setDate(QDate.currentDate())
        self.options_layout.addWidget(self.enddate)

        self.btn_globaldays_confirm = QPushButton(self.util.dict_language[self.language]['btn_confirm'])
        if self.btn_globaldays_function:
            self.btn_globaldays_confirm.clicked.connect(self.btn_globaldays_function)
        self.options_layout.addWidget(self.btn_globaldays_confirm)

    # create a child for frame_side_functions to have grid options
    def create_grid_options(self):
        self.clear_options_frame()
        lbl_initial_date = QLabel(self.util.dict_language[self.language]['lbl_init_dt'])
        self.options_layout.addWidget(lbl_initial_date)
        self.startdate = QDateEdit()
        self.startdate.setDisplayFormat('dd/MM/yyyy')
        self.startdate.setCalendarPopup(True)
        self.startdate.setDate(QDate.currentDate())
        self.options_layout.addWidget(self.startdate)

        lbl_final_date = QLabel(self.util.dict_language[self.language]['lbl_fin_dt'])
        self.options_layout.addWidget(lbl_final_date)
        self.enddate = QDateEdit()
        self.enddate.setDisplayFormat('dd/MM/yyyy')
        self.enddate.setCalendarPopup(True)
        self.enddate.setDate(QDate.currentDate())
        self.options_layout.addWidget(self.enddate)

        lbl_columns = QLabel(self.util.dict_language[self.language]['lbl_colum'])
        self.options_layout.addWidget(lbl_columns)
        self.columm_entry = QComboBox()
        self.columm_entry.setEditable(True)
        self.columm_entry.setInsertPolicy(QComboBox.NoInsert)
        self.options_layout.addWidget(self.columm_entry)

        lbl_rows = QLabel(self.util.dict_language[self.language]['lbl_row'])
        self.options_layout.addWidget(lbl_rows)
        self.row_entry = QComboBox()
        self.row_entry.setEditable(True)
        self.row_entry.setInsertPolicy(QComboBox.NoInsert)
        self.options_layout.addWidget(self.row_entry)

        self.btn_manydays_confirm = QPushButton(self.util.dict_language[self.language]['btn_confirm'])
        if self.btn_manydays_function:
            self.btn_manydays_confirm.clicked.connect(self.btn_manydays_function)
        self.options_layout.addWidget(self.btn_manydays_confirm)

    def add_subtractions_widget(self):
        lbl_minuend = QLabel(self.util.dict_language[self.language]['lbl_minuend'])
        self.options_layout.addWidget(lbl_minuend)
        self.minuend_stations_list = QListWidget()
        self.options_layout.addWidget(self.minuend_stations_list)
        lbl_subtracted = QLabel(self.util.dict_language[self.language]['lbl_subtracted'])
        self.options_layout.addWidget(lbl_subtracted)
        self.subtracted_stations_list = QListWidget()
        self.options_layout.addWidget(self.subtracted_stations_list)
        self.update_lists()

    # changes kind of options plotting
    def change_parameters(self, index):
        match index:
            case 0:
                self.create_oneday_options()
                self.list_all_stations.setSelectionMode(QAbstractItemView.MultiSelection)
            case 1:
                self.create_manydays_options()
                self.list_all_stations.setSelectionMode(QAbstractItemView.MultiSelection)
            case 2:
                self.create_grid_options()
                self.list_all_stations.setSelectionMode(QAbstractItemView.MultiSelection)
            case 3:
                self.create_manydays_options()
                self.list_all_stations.setSelectionMode(QAbstractItemView.MultiSelection)
            case 4:
                self.create_manydays_options()
                self.add_subtractions_widget()
                self.list_all_stations.setSelectionMode(QAbstractItemView.NoSelection)

    # update all info came from the chosen drive 
    def change_local(self, index):
        if self.local_downloads_function:
            self.local_downloads_function()

    # fill a listbox with the given data
    def populate_list_options(self, listwidget, stations):
        listwidget.clear()
        for i in stations:
            listwidget.addItem(i)

    # fill combobox that is chooses path
    def populate_combo_local(self):
        combo_list = []
        particoes = psutil.disk_partitions()
        for particao in particoes:
            combo_list.append(particao.device)
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

    def clear_options_frame(self):
        while self.options_layout.count():
            item = self.options_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()