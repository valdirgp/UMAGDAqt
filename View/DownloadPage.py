from PyQt5.QtWidgets import QWidget, QGridLayout
from View.Frames.SideOptionsDownload import SideOptionsDownload
from View.Frames.Map import Map
from General.util import Util
import re
import numpy as np

class DownloadPage(QWidget):
    def __init__(self, parent=None, language='en', magnetic_eq_coords=None):
        super().__init__(parent)
        self.lang = language
        self.magnetic_eq_coords = magnetic_eq_coords
        self.util = Util()

        self.selected_listbox = []
        self.all_locals = []
        self.colors = []

        self.embrace_stations = []
        self.intermagnet_stations = []

        self.layout = QGridLayout(self)
        self.setLayout(self.layout)

        # Criar SideOptions
        self.side_options = SideOptionsDownload(self, self.lang)
        self.layout.addWidget(self.side_options, 0, 0, 1, 1)

        # Referências rápidas para widgets
        self.list_all_stations = self.side_options.list_all_stations
        self.combo_download_location = self.side_options.combo_download_location
        self.ent_durationchosen = self.side_options.ent_durationchosen
        self.combo_durationtype = self.side_options.combo_durationtype
        self.cal_initial_date = self.side_options.cal_initial_date
        self.btn_confirm = self.side_options.btn_confirm
        self.btn_readme = self.side_options.btn_readme
        self.btn_select_all = self.side_options.btn_select_all
        self.btn_clear_all = self.side_options.btn_clear_all

        # Conectar botões de selecionar / limpar tudo
        self.btn_select_all.clicked.connect(self.set_all_selected)
        self.btn_clear_all.clicked.connect(self.set_all_clear)

        # Popular combo e lista
        self.populate_local_and_stations()

        # Criar Mapa
        self.map_widget = Map(self)
        self.layout.addWidget(self.map_widget, 0, 1, 1, 1)
        self.map_widget.all_locals = self.all_locals
        self.map_widget.create_map()
        self.map_widget.set_station_map(self.get_longitudes(), self.get_latitudes())
        self.map_widget.set_stationsname_map(self.all_locals)

        # Conectar seleção da lista ao mapa
        self.list_all_stations.itemSelectionChanged.connect(self.listbox_on_click)

    # ================= Map & List Control =================
    def set_all_selected(self):
        self.side_options.select_all_list()
        self.map_widget.select_all_points()

    def set_all_clear(self):
        self.side_options.clear_all_list()
        self.map_widget.clear_all_points()

    # ================= Stations Data =================
    def populate_local_and_stations(self):
        # Popula drives
        self.side_options.populate_combo_local()

        # Popula estações
        self.get_stations_location()
        stations_sorted = sorted(self.embrace_stations + self.intermagnet_stations)
        self.side_options.populate_stations_listbox(stations_sorted)

    def get_stations_location(self):
        self.all_locals = []
        self.longitude = []
        self.latitude = []

        try:
            with open('readme_stations.txt','r') as file:
                file_lines = file.read().split('\n')[1:-1]
                for line in file_lines:
                    try:
                        station_info = re.split(r'\s{2,}', line)
                        long, lat = float(station_info[2]), float(station_info[3])
                        if long > 180:
                            long -= 360.0
                        station_info[0] = 'VSE' if station_info[0] == 'VSS' and station_info[4] == 'EMBRACE' else station_info[0]
                        station_info[0] = 'VSI' if station_info[0] == 'VSS' and station_info[4] == 'INTERMAGNET' else station_info[0]

                        if station_info[0] in self.embrace_stations or station_info[0] in self.intermagnet_stations:
                            self.longitude.append(long)
                            self.latitude.append(lat)
                            self.all_locals.append({'station': station_info[0], 'longitude': long, 'latitude': lat})
                    except Exception as error:
                        print(error)
        except Exception:
            # Aviso caso arquivo não seja lido
            from PyQt5.QtWidgets import QLabel
            warning = QLabel(self.util.dict_language[self.lang]['lbl_noreadme'])
            self.layout.addWidget(warning, 99, 0, 1, 2)

    def get_longitudes(self):
        return [loc['longitude'] for loc in self.all_locals]

    def get_latitudes(self):
        return [loc['latitude'] for loc in self.all_locals]

    # ================= List & Map Interaction =================
    def listbox_on_click(self):
        itens_from_list = [self.list_all_stations.item(i).text() for i in range(self.list_all_stations.count())]
        selected_items = [item.text() for item in self.list_all_stations.selectedItems()]
        self.colors = []
        for local in self.all_locals:
            if local['station'] in selected_items:
                self.colors.append('lightgreen')
            else:
                self.colors.append('red')
        if hasattr(self.map_widget, 'scart'):
            self.map_widget.scart.set_facecolors(self.colors)
            self.map_widget.canvas.draw()

    # ================= Set Options Callback =================
    def set_embrace_options(self, callback):
        self.embrace_stations = callback

    def set_intermagnet_options(self, callback):
        self.intermagnet_stations = callback

    def bind_download(self, callback):
        self.btn_confirm.clicked.connect(callback)

    def bind_download_readme(self, callback):
        self.btn_readme.clicked.connect(callback)

    # ================= Getters =================
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

    def get_btn_confirm(self):
        return self.btn_confirm

    def get_btn_readme(self):
        return self.btn_readme
