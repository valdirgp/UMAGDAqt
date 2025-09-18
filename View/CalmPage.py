from View.Frames.SideOptionsCalm import SideOptionsCalm
from View.Frames.Map import Map
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel
from General.util import Util
import re
import cartopy.crs as ccrs
import numpy as np

class CalmPage(QWidget):
    def __init__(self, root, language, magnetic_eq_coords={"long":0, "lat":0, "dip":0}):
        super().__init__(root)
        self.root = root
        self.lang = language
        self.magnetic_eq_coords = magnetic_eq_coords
        self.util = Util()
        # Composição: instanciando componentes ao invés de herdar
        self.side_options = SideOptionsCalm(self, self.lang)
        self.map_widget = Map(self)
        self.downloaded_data_stations = []
        self.longitude = []
        self.latitude = []
        self.all_locals = []

    def ensure_array(self, y, x):
        """
        Garante que y seja um array do mesmo tamanho que x.
        Se y for um valor escalar, cria um array preenchido com esse valor.
        Se y for None ou vazio, cria um array de zeros.
        """
        if y is None:
            return np.zeros_like(x)
        elif np.isscalar(y):
            return np.full_like(x, y, dtype=float)
        else:
            y = np.array(y, dtype=float)
            if y.shape != x.shape:
                raise ValueError(f"y deve ter o mesmo tamanho que x. x:{x.shape}, y:{y.shape}")
            return y

    def create_page_frames(self):
        # Cria o layout principal horizontal
        #main_layout = QHBoxLayout(self.root)
        #self.root.setLayout(main_layout)

        if self.layout() is None:
            main_layout = QHBoxLayout(self)
            self.setLayout(main_layout)
        else:
            main_layout = self.layout()

        #self.destroy_all_frames()

        # Lado esquerdo: opções
        self.side_options.create_calm_plot_options()
        self.get_downloaded_stations_location()
        self.side_options.populate_list_options(self.side_options.list_all_stations, self.downloaded_data_stations)
        self.side_options.list_all_stations.itemSelectionChanged.connect(self.listbox_on_click)

        # Lado direito: mapa
        self.map_widget.create_map()
        self.map_widget.set_station_map(self.longitude, self.latitude)
        self.map_widget.set_stationsname_map(self.all_locals)
        '''self.map_widget.ax.contour(
            self.magnetic_eq_coords['long'],
            self.magnetic_eq_coords['lat'],
            self.magnetic_eq_coords['dip'],
            levels=[0], colors='gray'
        )'''

        longitudes = np.linspace(-180, 180, 361)

        # Se self.magnetic_eq_coords for um único valor, crie um array do mesmo tamanho
        y_values = self.ensure_array(self.magnetic_eq_coords, longitudes)
        
        self.map_widget.ax.plot(longitudes, y_values, color='gray', transform=ccrs.PlateCarree())

        self.map_widget.fig.canvas.mpl_connect('button_press_event', self.map_on_click)

        # Adiciona frames ao layout principal
        main_layout.addWidget(self.side_options.frame_side_functions_calm)
        main_layout.addWidget(self.map_widget.map_frame)

    '''
    def destroy_all_frames(self):
        # Destroi todos os frames existentes no root
        for child in self.root.findChildren(QWidget):
            if child is not self.root:
                child.setParent(None)
    '''
                
    def get_downloaded_stations_location(self):
        # Cria lista com dicionários de nome, longitude e latitude das estações
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
                            long = long - 360.0
                        if station_info[0] in self.downloaded_data_stations:
                            self.longitude.append(long)
                            self.latitude.append(lat)
                            self.all_locals.append({'station': station_info[0], 'longitude': long, 'latitude': lat})
        except Exception:
            warning = QLabel(self.util.dict_language[self.lang]['lbl_noreadme'])
            self.side_options.frame_side_functions_calm.inner_layout.addWidget(warning)

    def listbox_on_click(self):
        # Altera status do mapa quando a lista é selecionada
        selected_items = [item.text() for item in self.side_options.list_all_stations.selectedItems()]
        for i, local in enumerate(self.all_locals):
            if local['station'] in selected_items:
                self.map_widget.colors[i] = 'lightgreen'
            else:
                self.map_widget.colors[i] = 'red'
        self.map_widget.scart.set_facecolors(self.map_widget.colors)
        self.map_widget.canvas.draw()

    def map_on_click(self, event):
        # Altera status do mapa e da lista quando um ponto do mapa é clicado
        if event.inaxes is not None:
            selected_longitude, selected_latitude = event.xdata, event.ydata
            for i, local in enumerate(self.all_locals):
                if abs(selected_longitude - local['longitude']) < 1.0 and abs(selected_latitude - local['latitude']) < 1.0:
                    items = [self.side_options.list_all_stations.item(j).text() for j in range(self.side_options.list_all_stations.count())]
                    selection = items.index(local['station'])
                    item = self.side_options.list_all_stations.item(selection)
                    if self.map_widget.colors[i] == 'red':
                        item.setSelected(True)
                        self.map_widget.colors[i] = 'lightgreen'
                    else:
                        item.setSelected(False)
                        self.map_widget.colors[i] = 'red'
                    self.map_widget.scart.set_facecolors(self.map_widget.colors)
                    self.map_widget.canvas.draw()

    def can_be_number(self, number):
        # Verifica se uma string pode ser convertida para float
        try:
            float(number)
            return True
        except Exception:
            return False

    def update_data(self):
        self.side_options.list_all_stations.clear()
        self.side_options.populate_list_options(self.side_options.list_all_stations, self.downloaded_data_stations)
        for scatter in self.map_widget.scart_plots:
            scatter.remove()
        self.map_widget.scart_plots.clear()
        for text in self.map_widget.text_annotations:
            text.remove()
        self.map_widget.text_annotations.clear()

        self.get_downloaded_stations_location()
        self.map_widget.set_station_map(self.longitude, self.latitude)
        self.map_widget.set_stationsname_map(self.all_locals)
        self.map_widget.canvas.draw()

    def bind_plot_graph_H(self, callback):
        self.side_options.btn_plot_confirm_H.clicked.connect(callback)

    def bind_plot_graph_Z(self, callback):
        self.side_options.btn_plot_confirm_Z.clicked.connect(callback)

    def bind_search_stations_downloaded(self, callback):
        self.downloaded_data_stations = callback

    def bind_local_downloaded(self, callback):
        self.side_options.local_downloads_function = callback

    def get_start_date(self):
        return self.side_options.startdate.date().toPyDate()

    def get_end_date(self):
        return self.side_options.enddate.date().toPyDate()

    def get_selected_station(self):
        selected_items = self.side_options.list_all_stations.selectedItems()
        if selected_items:
            return selected_items[0].text()
        return None

    def get_selected_calm_dates(self):
        return self.side_options.selected_calm_dates

    def get_local_download(self):
        return self.side_options.combo_download_location.currentText()