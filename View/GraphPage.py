from PyQt5.QtWidgets import (
    QWidget, QLabel, QListWidget, QPushButton, QComboBox, QSpinBox, 
    QCheckBox, QVBoxLayout, QGridLayout, QCalendarWidget
)
from PyQt5.QtCore import Qt
from View.Frames.SideOptionsPlot import SideOptionsPlot
from View.Frames.Map import Map
from General.util import Util
import re
import numpy as np
import cartopy.crs as ccrs

class GraphPage(QWidget):
    def __init__(self, parent=None, language='en', magnetic_eq_coords=None):
        super().__init__(parent)
        self.lang = language
        self.magnetic_eq_coords = magnetic_eq_coords
        self.util = Util()

        # Herança simulada
        self.side_options = SideOptionsPlot(self, self.lang)
        self.map_widget = Map(self)  # cria o widget do mapa
        self.layout.addWidget(self.map_widget)  # adiciona ao layout do GraphPage


        # Widgets principais
        self.list_all_stations = QListWidget()
        self.minuend_stations_list = QListWidget()
        self.subtracted_stations_list = QListWidget()
        self.combo_type_plot = QComboBox()
        self.combo_download_location = QComboBox()
        self.startdate = QCalendarWidget()
        self.enddate = QCalendarWidget()
        self.columm_entry = QSpinBox()
        self.row_entry = QSpinBox()
        self.btn_singleday = QPushButton("Single Day")
        self.btn_globaldays = QPushButton("Global Days")
        self.btn_manydays = QPushButton("Many Days")
        self.btn_select_all = QPushButton("Select All")
        self.btn_clear_all = QPushButton("Clear All")
        self.is_dH = QCheckBox("dH")
        self.is_H = QCheckBox("H")
        self.is_dD = QCheckBox("dD")
        self.is_D = QCheckBox("D")
        self.is_dZ = QCheckBox("dZ")
        self.is_Z = QCheckBox("Z")
        self.is_dI = QCheckBox("dI")
        self.is_I = QCheckBox("I")
        self.is_dF = QCheckBox("dF")
        self.is_F = QCheckBox("F")
        self.is_dG = QCheckBox("dG")
        self.is_G = QCheckBox("G")
        self.is_dX = QCheckBox("dX")
        self.is_X = QCheckBox("X")
        self.is_dY = QCheckBox("dY")
        self.is_Y = QCheckBox("Y")
        self.is_reference = QCheckBox("Reference")
        self.is_bold_text = QCheckBox("Bold Text")
        self.is_grid_graph = QCheckBox("Grid Graph")

        # Layout
        self.layout = QGridLayout(self)
        self.setLayout(self.layout)

        # Configuração inicial
        self.create_page_frames()

    def create_page_frames(self):
        self.layout.addWidget(QLabel("Stations:"), 0, 0)
        self.layout.addWidget(self.list_all_stations, 1, 0, 1, 2)
        self.layout.addWidget(self.btn_select_all, 2, 0)
        self.layout.addWidget(self.btn_clear_all, 2, 1)
        self.layout.addWidget(self.combo_download_location, 3, 0, 1, 2)

        self.get_downloaded_stations_location()
        self.map_widget.create_map()
        self.map_widget.set_station_map(self.longitude, self.latitude)
        self.map_widget.set_stationsname_map(self.all_locals)

        longitudes = np.linspace(-180, 180, 361)
        self.map_widget.ax.plot(longitudes, self.magnetic_eq_coords, color='gray', transform=ccrs.PlateCarree())
        self.map_widget.canvas.mpl_connect('button_press_event', self.map_on_click)

        self.list_all_stations.itemSelectionChanged.connect(self.listbox_on_click)
        self.btn_select_all.clicked.connect(self.set_all_selected)
        self.btn_clear_all.clicked.connect(self.set_all_clear)

    def set_all_selected(self):
        self.select_all_list()
        self.select_all_points()

    def set_all_clear(self):
        self.clear_all_list()
        self.clear_all_points()

    def get_downloaded_stations_location(self):
        self.all_locals = []
        self.longitude = []
        self.latitude = []

        try:
            with open('readme_stations.txt', 'r') as file:
                file_lines = file.read().split('\n')[1:-1]
                for line in file_lines:
                    try:
                        station_info = re.split(r'\s{2,}', line)
                        long, lat = float(station_info[2]), float(station_info[3])
                        if long > 180: long -= 360.0
                        if station_info[0] in getattr(self, 'downloaded_data_stations', []):
                            self.longitude.append(long)
                            self.latitude.append(lat)
                            self.all_locals.append({'station': station_info[0], 'longitude': long, 'latitude': lat})
                    except Exception as e:
                        print(e)
        except Exception:
            warning = QLabel(self.util.dict_language[self.lang]['lbl_noreadme'])
            self.layout.addWidget(warning, 99, 0, 1, 2)

    def listbox_on_click(self):
        itens_from_list = [item.text() for item in self.list_all_stations.selectedItems()]
        self.colors = getattr(self, 'colors', ['red'] * len(self.all_locals))
        for i, local in enumerate(self.all_locals):
            if self.colors[i] == 'red' and local['station'] in itens_from_list:
                self.colors[i] = 'lightgreen'
            elif self.colors[i] == 'lightgreen' and local['station'] not in itens_from_list:
                self.colors[i] = 'red'
        self.map_widget.scart.set_facecolors(self.colors)
        self.map_widget.canvas.draw()

    def map_on_click(self, event):
        if event.inaxes is not None:
            selected_longitude, selected_latitude = event.xdata, event.ydata
            self.colors = getattr(self, 'colors', ['red'] * len(self.all_locals))
            for i, local in enumerate(self.all_locals):
                if abs(selected_longitude - local['longitude']) < 1.0 and abs(selected_latitude - local['latitude']) < 1.0:
                    items = self.list_all_stations.findItems(local['station'], Qt.MatchExactly)
                    if self.colors[i] == 'red':
                        if items: items[0].setSelected(True)
                        self.colors[i] = 'lightgreen'
                    else:
                        if items: items[0].setSelected(False)
                        self.colors[i] = 'red'
                    self.map_widget.scart.set_facecolors(self.colors)
                    self.map_widget.canvas.draw()

    def update_data(self):
        self.list_all_stations.clear()
        self.populate_list_options(self.list_all_stations, getattr(self, 'downloaded_data_stations', []))
        for scatter in getattr(self.map_widget, 'scart_plots', []):
            scatter.remove()
        self.map_widget.scart_plots = []
        for text in getattr(self.map_widget, 'text_annotations', []):
            text.remove()
        self.map_widget.text_annotations = []

        self.get_downloaded_stations_location()
        self.set_station_map(self.longitude, self.latitude)
        self.set_stationsname_map(self.all_locals)
        self.map_widget.canvas.draw()

    # Métodos de binding e getters (mantidos conforme Tkinter)
    def bind_single_graph(self, callback): self.btn_singleday.clicked.connect(callback)
    def bind_global_graph(self, callback): self.btn_globaldays.clicked.connect(callback)
    def bind_many_graphs(self, callback): self.btn_manydays.clicked.connect(callback)
    def bind_search_stations_downloaded(self, callback): self.downloaded_data_stations = callback
    def bind_local_downloaded(self, callback): self.update_downloaded_local = callback
    def get_local_download(self): return self.combo_download_location.currentText()
    def get_stations_selected(self): return [self.list_all_stations.item(i).text() for i in range(self.list_all_stations.count()) if self.list_all_stations.item(i).isSelected()]
