from View.Frames.SideOptionsDownload import SideOptionsDownload
from View.Frames.Map import Map
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel
import re
from General.util import Util
import cartopy.crs as ccrs
import numpy as np


class DownloadPage(QWidget):
    def __init__(self, root, language, year, drive, magnetic_eq_coords):
        super().__init__(root)
        self.root = root
        self.lang = language
        self.year = year
        self.drive = drive
        self.magnetic_eq_coords = magnetic_eq_coords

        self.selected_listbox = []
        self.all_locals = []
        self.colors = []

        self.util = Util()
        self.side_options = SideOptionsDownload(self, self.lang, self.year, self.drive)  # importante: agora passa "self"
        self.map_widget = Map(self)                               # idem
        self.embrace_stations = []
        self.intermagnet_stations = []

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

    # cria frames principais
    def create_page_frames(self):
        # Layout principal no PRÓPRIO widget
        #main_layout = QHBoxLayout(self)
        #self.setLayout(main_layout)

        if self.layout() is None:
            main_layout = QHBoxLayout(self)
            self.setLayout(main_layout)
        else:
            main_layout = self.layout()  # usa o layout já existente


        #self.util.destroy_existent_frames(self)

        self.side_options.create_download_options()
        self.side_options.btn_select_all.clicked.connect(self.set_all_selected)
        self.side_options.btn_clear_all.clicked.connect(self.set_all_clear)
        self.side_options.populate_combo_local()
        self.side_options.populate_stations_listbox(
            self.side_options.list_all_stations,
            sorted(self.embrace_stations + self.intermagnet_stations)
        )
        self.side_options.list_all_stations.itemSelectionChanged.connect(self.listbox_on_click)

        self.map_widget.create_map()
        self.get_stations_location()
        # inicializa as cores com base nas estações carregadas
        self.colors = ['red'] * len(self.all_locals)
        self.map_widget.set_station_map(self.longitude, self.latitude)
        self.map_widget.set_stationsname_map(self.all_locals)

        longitudes = np.linspace(-180, 180, 361)
        y_values = self.ensure_array(self.magnetic_eq_coords, longitudes)
        self.map_widget.ax.plot(longitudes, y_values, color='#4B4B4B', transform=ccrs.PlateCarree())
        self.map_widget.ax.plot(longitudes, y_values * 0, color='#7A7A7A', transform=ccrs.PlateCarree())

        # se magnetic_eq_coords for escalar, converta para array do mesmo tamanho
        '''if np.isscalar(self.magnetic_eq_coords):
            latitudes = np.full_like(longitudes, self.magnetic_eq_coords, dtype=float)
        else:
            latitudes = np.array(self.magnetic_eq_coords, dtype=float)
            if latitudes.shape != longitudes.shape:
                raise ValueError("magnetic_eq_coords deve ter o mesmo tamanho que longitudes")

        # desenha a linha do equador magnético
        self.map_widget.ax.plot(longitudes, latitudes, color='gray', linewidth=2, transform=ccrs.Geodetic())'''

        self.map_widget.fig.canvas.mpl_connect('button_press_event', self.map_on_click)

        main_layout.addWidget(self.side_options.options_frame)
        main_layout.addWidget(self.map_widget.map_frame)

    # select all stations from map and listbox
    def set_all_selected(self):
        self.side_options.select_all_list()
        self.map_widget.select_all_points()

    # clear all selected stations from map and listbox
    def set_all_clear(self):
        self.side_options.clear_all_list()
        self.map_widget.clear_all_points()

    # makes a list with all dictionary with station's name, longitude and latitude
    def get_stations_location(self):
        self.all_locals = []
        self.longitude = []
        self.latitude = []

        '''try:
            with open('readme_stations.txt','r') as file: 
                file_lines = file.read().split('\n')[1:-1]
                for line in file_lines:
                    try:
                        station_info = re.split(r'\s{2,}', line)
                        long, lat = float(station_info[2]), float(station_info[3])
                        if long > 180:
                            long = long - 360.0
                        station_info[0] = 'VSE' if station_info[0] == 'VSS' and station_info[4] == 'EMBRACE' else station_info[0]
                        station_info[0] = 'VSI' if station_info[0] == 'VSS' and station_info[4] == 'INTERMAGNET' else station_info[0]
                        if station_info[0] in self.embrace_stations or station_info[0] in self.intermagnet_stations:
                            self.longitude.append(long)
                            self.latitude.append(lat)
                            self.all_locals.append({'station': station_info[0], 'longitude': long, 'latitude': lat})
                    except Exception as error:
                        print(error)
                print(self.all_locals)
        except Exception:
            warning = QLabel(self.util.dict_language[self.lang]['lbl_noreadme'])
            self.side_options.options_frame.inner_frame.layout().addWidget(warning)'''
        
        for i in range(self.side_options.list_all_stations.count()):
            item = self.side_options.list_all_stations.item(i)
            
            text = item.text()
            # Regex para capturar SIGLA, latitude, longitude e dip
            match = re.match(r'^([A-Z]{3}) \(([-\d.]+), ([-\d.]+), ([-\d.]+)\)', text)
            if match:
                sigla = match.group(1)
                lat = float(match.group(2))
                lon = float(match.group(3))
                
                self.latitude.append(lat)
                self.longitude.append(lon)
                self.all_locals.append({'station': sigla, 'latitude': lat, 'longitude': lon})
            
    # change map's status when listbox is selected
    def listbox_on_click(self):
        """items_from_list = [self.side_options.list_all_stations.item(i).text() for i in range(self.side_options.list_all_stations.count())]
        '''items_from_list = [
                                re.match(r'^([A-Z]{3})', self.side_options.list_all_stations.item(i).text()).group(1)
                                for i in range(self.side_options.list_all_stations.count())
                        ]'''

        selected_indexes = [i for i in range(self.side_options.list_all_stations.count()) if self.side_options.list_all_stations.item(i).isSelected()]
        self.colors = ['red'] * len(self.all_locals)
        for i, local in enumerate(self.all_locals):
            try:
                selection = items_from_list.index(local['station'])
                if selection in selected_indexes:
                    self.colors[i] = 'lightgreen'
            except ValueError:
                continue
        if hasattr(self.map_widget, 'scart'):
            self.map_widget.scart.set_facecolors(self.colors)
            self.map_widget.canvas.draw()"""
        
        # Altera status do mapa quando a lista é selecionada
        selected_items = [item.text() for item in self.side_options.list_all_stations.selectedItems()]
        '''for i, local in enumerate(self.all_locals):
            if local['station'] in selected_items:
                self.map_widget.colors[i] = 'lightgreen'
            else:
                self.map_widget.colors[i] = 'red'''
        for i, local in enumerate(self.all_locals):
            if any(item.startswith(f"{local['station']} ") for item in selected_items):
                self.map_widget.colors[i] = 'lightgreen'
            else:
                self.map_widget.colors[i] = 'red'
        self.map_widget.scart.set_facecolors(self.map_widget.colors)
        self.map_widget.canvas.draw()

    # change map's status and listbox's status when map's button is selected
    def map_on_click(self, event):
        '''if event.inaxes is not None:
            selected_longitude, selected_latitude = event.xdata, event.ydata
            items_from_list = [self.side_options.list_all_stations.item(i).text() for i in range(self.side_options.list_all_stations.count())]
            for i, local in enumerate(self.all_locals):
                if abs(selected_longitude - local['longitude']) < 1.0 and abs(selected_latitude - local['latitude']) < 1.0:
                    try:
                        selection = items_from_list.index(local['station'])
                        item = self.side_options.list_all_stations.item(selection)
                        if self.colors[i] == 'red':
                            item.setSelected(True)
                            self.colors[i] = 'lightgreen'
                        else:
                            item.setSelected(False)
                            self.colors[i] = 'red'
                        if hasattr(self.map_widget, 'scart'):
                            self.map_widget.scart.set_facecolors(self.colors)
                            self.map_widget.canvas.draw()
                    except ValueError:
                        continue'''
        
        """from math import hypot

        if event.inaxes is not None:
            selected_longitude, selected_latitude = event.xdata, event.ydata
            #items_from_list = [self.side_options.list_all_stations.item(i).text() for i in range(self.side_options.list_all_stations.count())]
            items_from_list = [
                                re.match(r'^([A-Z]{3})', self.side_options.list_all_stations.item(i).text()).group(1)
                                for i in range(self.side_options.list_all_stations.count())
                            ]

            # calcula a distância euclidiana em graus e encontra o ponto mais próximo
            distances = [
                (i, hypot(selected_longitude - local['longitude'], selected_latitude - local['latitude']))
                for i, local in enumerate(self.all_locals)
            ]

            nearest_index, min_dist = min(distances, key=lambda x: x[1])

            # define a tolerância (em graus)
            tolerance = 0.5

            if min_dist < tolerance:
                local = self.all_locals[nearest_index]
                try:
                    selection = items_from_list.index(local['station'])
                    item = self.side_options.list_all_stations.item(selection)
                    if self.colors[nearest_index] == 'red':
                        item.setSelected(True)
                        self.colors[nearest_index] = 'lightgreen'
                    else:
                        item.setSelected(False)
                        self.colors[nearest_index] = 'red'
                    if hasattr(self.map_widget, 'scart'):
                        self.map_widget.scart.set_facecolors(self.colors)
                        self.map_widget.canvas.draw()
                except ValueError:
                    pass"""
        
        # Altera status do mapa e da lista quando um ponto do mapa é clicado
        if event.inaxes is not None:
            selected_longitude, selected_latitude = event.xdata, event.ydata
            for i, local in enumerate(self.all_locals):
                if abs(selected_longitude - local['longitude']) < 1.0 and abs(selected_latitude - local['latitude']) < 1.0:
                    items = [self.side_options.list_all_stations.item(j).text() for j in range(self.side_options.list_all_stations.count())]
                    #selection = items.index(local['station'])
                    selection = next(i for i, item in enumerate(items) if item.startswith(f"{local['station']} "))
                    item = self.side_options.list_all_stations.item(selection)
                    if self.map_widget.colors[i] == 'red':
                        item.setSelected(True)
                        self.map_widget.colors[i] = 'lightgreen'
                    else:
                        item.setSelected(False)
                        self.map_widget.colors[i] = 'red'
                    self.map_widget.scart.set_facecolors(self.map_widget.colors)
                    self.map_widget.canvas.draw()

    def set_embrace_options(self, callback):
        self.embrace_stations = callback

    def set_intermagnet_options(self, callback):
        self.intermagnet_stations = callback    

    def bind_download(self, callback):
        self.side_options.btn_confirm.clicked.connect(callback)

    def bind_download_readme(self, callback):
        self.side_options.btn_readme.clicked.connect(callback)

    def get_options_frame(self):
        return self.side_options.options_frame

    def get_local_download(self):
        return self.side_options.combo_download_location.currentText()


    def get_stations_selected(self):
        selected_stations = set()
        for i in range(self.side_options.list_all_stations.count()):
            item = self.side_options.list_all_stations.item(i)
            if item.isSelected():
                selected_stations.add((item.text())[0].split())
        return list(selected_stations)

    '''def get_stations_selected(self):
        selected_stations = set()
        for i in range(self.side_options.list_all_stations.count()):
            item = self.side_options.list_all_stations.item(i)
            if item.isSelected():
                # extrai apenas o código da estação (os 3 primeiros caracteres)
                code = item.text()[:3]
                selected_stations.add(code)
        return list(selected_stations)'''
        
    def get_duration_chosen(self):
        return self.side_options.ent_durationchosen.text()

    def get_duration_type(self):
        return self.side_options.combo_durationtype.currentIndex()

    def get_date(self):
        return self.side_options.cal_initial_date.date().toPyDate()

    def get_btn_confirm(self):
        return self.side_options.btn_confirm

    def get_btn_readme(self):
        return self.side_options.btn_readme