from Model.Custom.CustomttkFrame import ScrollableFrame
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QListWidget, QAbstractItemView,
    QPushButton, QDateEdit, QSizePolicy, QScrollBar, QLineEdit, QListWidgetItem
)
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtGui import QIntValidator, QDoubleValidator
import psutil
from General.util import Util

class SideOptionsDownload(QWidget):
    def __init__(self, root, language, year, drive):
        super().__init__(root)
        self.language = language
        self.year = year
        self.drive = drive
        self.util = Util()
        self.options_frame = None

    # Função de filtro
    def filter_visible_items(self):
        def parse_val(text):
            try:
                if not text: return None
                return float(text.replace(',', '.'))
            except ValueError:
                return None

        try:
            lat_min = parse_val(self.lat_min.text())
            lat_max = parse_val(self.lat_max.text())
            lon_min = parse_val(self.lon_min.text())
            lon_max = parse_val(self.lon_max.text())
            dip_min = parse_val(self.dip_min.text())
            dip_max = parse_val(self.dip_max.text())
            search_text = self.search_input.text().lower()
        except AttributeError:
            # Caso os widgets ainda não tenham sido criados
            return

        for i in range(self.list_all_stations.count()):
            item = self.list_all_stations.item(i)
            txt = item.text()
            # Formato esperado: "CODE (lat, lon, dip)"
            hidden = False
            if search_text and search_text not in txt.lower():
                hidden = True

            if not hidden:
                try:
                    start = txt.find('(')
                    end = txt.find(')')
                    if start != -1 and end != -1:
                        parts = txt[start+1:end].split(',')
                        if len(parts) >= 3:
                            lat = float(parts[0])
                            lon = float(parts[1])
                            dip = float(parts[2])

                            if lat_min is not None and lat < lat_min: hidden = True
                            if lat_max is not None and lat > lat_max: hidden = True
                            if lon_min is not None and lon < lon_min: hidden = True
                            if lon_max is not None and lon > lon_max: hidden = True
                            if dip_min is not None and dip < dip_min: hidden = True
                            if dip_max is not None and dip > dip_max: hidden = True
                except ValueError:
                    pass
            item.setHidden(hidden)

    def set_filter_values(self, lat_min, lat_max, lon_min, lon_max):
        self.lat_min.blockSignals(True)
        self.lat_max.blockSignals(True)
        self.lon_min.blockSignals(True)
        self.lon_max.blockSignals(True)

        self.lat_min.setText(f"{lat_min:.2f}")
        self.lat_max.setText(f"{lat_max:.2f}")
        self.lon_min.setText(f"{lon_min:.2f}")
        self.lon_max.setText(f"{lon_max:.2f}")

        self.lat_min.blockSignals(False)
        self.lat_max.blockSignals(False)
        self.lon_min.blockSignals(False)
        self.lon_max.blockSignals(False)
        
        self.filter_visible_items()


    # create download widget
    def create_download_options(self):
        # Parent do ScrollableFrame agora é self, e não DownloadPage

        # Antes era fixo em 255. Agora permitimos que encolha até 200 e cresça até 380.
        self.options_frame = ScrollableFrame(self, 200, 380)
        layout = self.options_frame.inner_layout  # pega o layout do scroll
        layout.setContentsMargins(5,5,5,5)
        layout.setSpacing(8)

        # Drive selection
        lbl_drive = QLabel(self.util.dict_language[self.language]["lbl_dr"])
        layout.addWidget(lbl_drive)
        self.combo_download_location = QComboBox()
        self.populate_combo_local()
        layout.addWidget(self.combo_download_location)

        # Search text
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Filtrar por texto...")
        self.search_input.textChanged.connect(self.filter_visible_items)
        layout.addWidget(self.search_input)

        # Filtros Lat/Lon/Dip
        filter_layout = QVBoxLayout()
        filter_layout.setSpacing(2)

        # Latitude
        row_lat = QHBoxLayout()
        row_lat.addWidget(QLabel("Lat:"))
        self.lat_min = QLineEdit(); self.lat_min.setPlaceholderText("Min"); self.lat_min.setValidator(QDoubleValidator())
        self.lat_max = QLineEdit(); self.lat_max.setPlaceholderText("Max"); self.lat_max.setValidator(QDoubleValidator())
        row_lat.addWidget(self.lat_min); row_lat.addWidget(self.lat_max)
        filter_layout.addLayout(row_lat)

        # Longitude
        row_lon = QHBoxLayout()
        row_lon.addWidget(QLabel("Lon:"))
        self.lon_min = QLineEdit(); self.lon_min.setPlaceholderText("Min"); self.lon_min.setValidator(QDoubleValidator())
        self.lon_max = QLineEdit(); self.lon_max.setPlaceholderText("Max"); self.lon_max.setValidator(QDoubleValidator())
        row_lon.addWidget(self.lon_min); row_lon.addWidget(self.lon_max)
        filter_layout.addLayout(row_lon)

        # Dip
        row_dip = QHBoxLayout()
        row_dip.addWidget(QLabel("Dip:"))
        self.dip_min = QLineEdit(); self.dip_min.setPlaceholderText("Min"); self.dip_min.setValidator(QDoubleValidator())
        self.dip_max = QLineEdit(); self.dip_max.setPlaceholderText("Max"); self.dip_max.setValidator(QDoubleValidator())
        row_dip.addWidget(self.dip_min); row_dip.addWidget(self.dip_max)
        filter_layout.addLayout(row_dip)

        layout.addLayout(filter_layout)

        # Conectar sinais
        for w in [self.lat_min, self.lat_max, self.lon_min, self.lon_max, self.dip_min, self.dip_max]:
            w.textChanged.connect(self.filter_visible_items)

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
        self.ent_durationchosen.setText("0")
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
        hoje = QDate.currentDate()
        data = QDate(self.year[2], self.year[1], self.year[0])
        self.cal_initial_date.setDate(data)
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
        selecionados = [item.text() for item in listwidget.selectedItems()]
        listwidget.clear()
        for st in stations:
            codigo = st.split()[0]   # pega só o código da estação (ex: "ARA")
            texto  = st              # texto completo (ex: "ARA (lat, lon, dip)")

            item = QListWidgetItem(texto)   # o que aparece na lista
            item.setData(Qt.UserRole, codigo)  # dado "oculto", só o código
            listwidget.addItem(item)
            if any(sel.startswith(codigo) for sel in selecionados):
                selecionar = listwidget.findItems(codigo, Qt.MatchContains)
                selecionar[0].setSelected(True)
                print(selecionar)
        self.filter_visible_items()

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

        index = self.combo_download_location.findText(self.drive)
        self.combo_download_location.setCurrentIndex(index)

    # select all station's list
    def select_all_list(self):
        self.list_all_stations.blockSignals(True)
        for i in range(self.list_all_stations.count()):
            item = self.list_all_stations.item(i)
            if not item.isHidden():
                item.setSelected(True)
        self.list_all_stations.blockSignals(False)
        self.list_all_stations.itemSelectionChanged.emit()

    # clear all station's list
    def clear_all_list(self):
        self.list_all_stations.blockSignals(True)
        for i in range(self.list_all_stations.count()):
            item = self.list_all_stations.item(i)
            if not item.isHidden():
                item.setSelected(False)
        self.list_all_stations.blockSignals(False)
        self.list_all_stations.itemSelectionChanged.emit()