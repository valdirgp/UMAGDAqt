from PyQt5.QtWidgets import QWidget, QLabel, QListWidget, QVBoxLayout, QGridLayout, QPushButton, QComboBox
from PyQt5.QtCore import Qt
from View.Frames.SideOptionsCalm import SideOptionsCalm
from View.Frames.Map import Map
from General.util import Util
import re

class CalmPage(QWidget):
    def __init__(self, parent=None, language='en', magnetic_eq_coords=None):
        super().__init__(parent)
        self.lang = language
        self.side_options = SideOptionsCalm(self, self.lang)
        self.map_widget = Map(self)
        self.magnetic_eq_coords = magnetic_eq_coords
        self.util = Util()
        #SideOptionsCalm.__init__(self, parent, self.lang)
        #Map.__init__(self, parent)
        self.init_ui()

    def init_ui(self):
        self.layout = QGridLayout(self)
        self.setLayout(self.layout)

        # Adiciona SideOptions e Map no layout
        self.layout.addWidget(self.side_options, 0, 0)
        self.layout.addWidget(self.map_widget, 0, 1)

        # Lista de estações
        self.list_all_stations = QListWidget()
        self.downloaded_data_stations = []
        self.side_options.populate_list_options(self.list_all_stations, self.downloaded_data_stations)
        self.list_all_stations.itemSelectionChanged.connect(self.listbox_on_click)
        self.layout.addWidget(self.list_all_stations, 1, 0)

        # Botão de plot
        self.btn_plot_confirm = self.side_options.btn_plot_confirm
        self.layout.addWidget(self.btn_plot_confirm, 2, 0)

        # Combobox de local de download
        self.combo_download_location = self.side_options.combo_download_location
        self.layout.addWidget(self.combo_download_location, 3, 0)

        # Criar mapa
        self.all_locals = []
        self.longitude = []
        self.latitude = []
        self.colors = []
        self.downloaded_data_stations = []

        self.map_widget.create_map()
        self.map_widget.set_station_map(self.longitude, self.latitude)
        self.map_widget.set_stationsname_map(self.all_locals)


        # Contorno do equador magnético, só se for dict
        if isinstance(self.magnetic_eq_coords, dict):
            self.map_widget.ax.contour(
                self.magnetic_eq_coords['long'],
                self.magnetic_eq_coords['lat'],
                self.magnetic_eq_coords['dip'],
                levels=[0],
                colors='gray'
            )
        self.map_widget.canvas.mpl_connect('button_press_event', self.map_on_click)


    def get_downloaded_stations_location(self):
        self.all_locals = []
        self.longitude = []
        self.latitude = []

        try:
            with open('readme_stations.txt', 'r') as file:
                file_lines = file.read().split('\n')[1:-1]
                for line in file_lines:
                    station_info = re.split(r'\s{2,}', line)
                    if self.can_be_number(station_info[2]) and self.can_be_number(station_info[3]):
                        long, lat = float(station_info[2]), float(station_info[3])
                        if long > 180:
                            long -= 360.0
                        if station_info[0] in self.downloaded_data_stations:
                            self.longitude.append(long)
                            self.latitude.append(lat)
                            self.all_locals.append({'station': station_info[0], 'longitude': long, 'latitude': lat})
        except Exception:
            warning = QLabel(self.util.dict_language[self.lang]['lbl_noreadme'])
            self.layout.addWidget(warning, 3, 0, 1, 2)

    def listbox_on_click(self):
        for i, local in enumerate(self.all_locals):
            selected_items = [item.text() for item in self.list_all_stations.selectedItems()]
            if self.colors[i] == 'red' and local['station'] in selected_items:
                self.colors[i] = 'lightgreen'
            elif self.colors[i] == 'lightgreen' and local['station'] not in selected_items:
                self.colors[i] = 'red'

        self.scart.set_facecolors(self.colors)
        self.canvas.draw()

    def map_on_click(self, event):
        if event.inaxes is not None:
            selected_longitude, selected_latitude = event.xdata, event.ydata
            for i, local in enumerate(self.all_locals):
                if abs(selected_longitude - local['longitude']) < 1.0 and abs(selected_latitude - local['latitude']) < 1.0:
                    items = self.list_all_stations.findItems(local['station'], Qt.MatchExactly)
                    if self.colors[i] == 'red':
                        if items:
                            items[0].setSelected(True)
                        self.colors[i] = 'lightgreen'
                    else:
                        if items:
                            items[0].setSelected(False)
                        self.colors[i] = 'red'

                    self.scart.set_facecolors(self.colors)
                    self.canvas.draw()

    def can_be_number(self, value):
        try:
            float(value)
            return True
        except ValueError:
            return False

    def update_data(self):
        self.list_all_stations.clear()
        self.populate_list_options(self.list_all_stations, self.downloaded_data_stations)
        for scatter in self.scart_plots:
            scatter.remove()
        self.scart_plots.clear()
        for text in self.text_annotations:
            text.remove()
        self.text_annotations.clear()

        self.get_downloaded_stations_location()
        self.set_station_map(self.longitude, self.latitude)
        self.set_stationsname_map(self.all_locals)
        self.canvas.draw()

    # Bindings
    def bind_plot_graph(self, callback):
        self.btn_plot_confirm.clicked.connect(callback)

    def bind_search_stations_downloaded(self, callback):
        self.downloaded_data_stations = callback

    def bind_local_downloaded(self, callback):
        self.local_downloads_function = callback

    # Getters
    def get_start_date(self):
        return self.startdate.date()

    def get_end_date(self):
        return self.enddate.date()

    def get_selected_station(self):
        items = self.list_all_stations.selectedItems()
        return items[0].text() if items else None

    def get_selected_calm_dates(self):
        return self.selected_calm_dates

    def get_local_download(self):
        return self.combo_download_location.currentText()
