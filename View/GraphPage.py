from View.Frames.SideOptionsPlot import SideOptionsPlot
from View.Frames.Map import Map
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt
import re
from General.util import Util
import cartopy.crs as ccrs
import numpy as np



class GraphPage(QWidget):
    def __init__(self, root, language, year, drive, magnetic_eq_coords=0):
        super().__init__(root)
        self.root = root
        self.lang = language
        self.year = year
        self.drive = drive
        self.magnetic_eq_coords = magnetic_eq_coords

        self.util = Util()
        self.side_options = SideOptionsPlot(self, self.lang, self.year, self.drive)
        self.map_widget = Map(self)

        self.downloaded_data_stations = []
        self.colors = []
        self.all_locals = []
        self.longitude = []
        self.latitude = []

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


    # creates frames for the tool
    def create_page_frames(self):
        # Layout principal horizontal
        #main_layout = QHBoxLayout(self.root)
        #self.setLayout(main_layout)
        if self.layout() is None:
            main_layout = QHBoxLayout(self)
            self.setLayout(main_layout)
        else:
            main_layout = self.layout()  # usa o layout já existente


        #self.util.destroy_existent_frames(self.root)

        self.side_options.create_plot_options()
        self.side_options.btn_select_all.clicked.connect(self.set_all_selected)
        self.side_options.btn_clear_all.clicked.connect(self.set_all_clear)

        self.side_options.populate_list_options(self.side_options.list_all_stations, self.downloaded_data_stations)
        self.side_options.list_all_stations.itemSelectionChanged.connect(self.listbox_on_click)
        self.side_options.update_lists = self.update_min_sub_list

        self.get_downloaded_stations_location()
        self.map_widget.create_map()
        self.colors = ['red'] * len(self.all_locals)
        self.map_widget.set_station_map(self.longitude, self.latitude)
        self.map_widget.set_stationsname_map(self.all_locals)

        longitudes = np.linspace(-180, 180, 361)

        # Se self.magnetic_eq_coords for um único valor, crie um array do mesmo tamanho
        y_values = self.ensure_array(self.magnetic_eq_coords, longitudes)
        
        self.map_widget.ax.plot(longitudes, y_values, color='gray', transform=ccrs.PlateCarree())
        self.map_widget.ax.plot(longitudes, y_values * 0, color='gray', transform=ccrs.PlateCarree())

        self.map_widget.fig.canvas.mpl_connect('button_press_event', self.map_on_click)

        main_layout.addWidget(self.side_options.frame_side_functions)
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
    def get_downloaded_stations_location(self):
        self.all_locals = []
        self.longitude = []
        self.latitude = []

        """
        try:
            with open('readme_stations.txt','r') as file: 
                file_lines = file.read().split('\n')[1:-1]
                for line in file_lines:
                    try:
                        station_info = re.split(r'\s{2,}', line)
                        long, lat = float(station_info[2]), float(station_info[3])
                        if long > 180:
                            long = long - 360.0
                        if station_info[0] in self.downloaded_data_stations:
                            self.longitude.append(long)
                            self.latitude.append(lat)
                            self.all_locals.append({'station': station_info[0], 'longitude': long, 'latitude': lat})
                    except Exception as error:
                        print(error)
        except Exception:
            warning = QLabel(self.util.dict_language[self.lang]['lbl_noreadme'])
            self.side_options.frame_side_functions.inner_frame.layout().addWidget(warning)
        """
        
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
        '''
        items_from_list = [self.side_options.list_all_stations.item(i).text() for i in range(self.side_options.list_all_stations.count())]
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
            self.map_widget.canvas.draw()
        '''
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
        '''
        if event.inaxes is not None:
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
                        continue
        '''

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

    # update all appearing widgets
    def update_data(self):
        self.side_options.list_all_stations.clear()
        self.side_options.populate_list_options(self.side_options.list_all_stations, self.downloaded_data_stations)
        self.side_options.update_lists = self.update_min_sub_list
        for scatter in self.map_widget.scart_plots:
            scatter.remove()
        self.map_widget.scart_plots.clear()
        for text in self.map_widget.text_annotations:
            text.remove()
        self.map_widget.text_annotations.clear() 
        
        self.get_downloaded_stations_location()
        self.map_widget.set_station_map(self.longitude, self.latitude)
        self.map_widget.set_stationsname_map(self.all_locals)

        longitudes = np.linspace(-180, 180, 361)

        y_values = self.ensure_array(self.magnetic_eq_coords, longitudes)

        self.map_widget.ax.plot(longitudes, y_values, color='gray', transform=ccrs.PlateCarree())

        self.map_widget.canvas.draw()

    def update_min_sub_list(self):
        self.side_options.populate_list_options(self.side_options.minuend_stations_list, self.downloaded_data_stations)
        self.side_options.populate_list_options(self.side_options.subtracted_stations_list, self.downloaded_data_stations)

    def onfile_changed(self, path):
        self.side_options.list_all_stations.clear()
        self.side_options.populate_list_options(self.side_options.list_all_stations, self.downloaded_data_stations)

    def bind_single_graph(self, callback):
        self.side_options.btn_singleday_function = callback

    def bind_global_graph(self, callback):
        self.side_options.btn_globaldays_function = callback

    def bind_many_graphs(self, callback):
        self.side_options.btn_manydays_function = callback

    def bind_search_stations_downloaded(self, callback):
        self.downloaded_data_stations = callback

    def bind_local_downloaded(self, callback):
        self.side_options.local_downloads_function = callback

    def get_local_download(self):
        return self.side_options.combo_download_location.currentText()

    def get_stations_selected(self):
        selected_stations = set()
        for i in range(self.side_options.list_all_stations.count()):
            item = self.side_options.list_all_stations.item(i)
            if item.isSelected():
                #selected_stations.add(item.text())
                selected_stations.add(item.data(Qt.UserRole))
        return list(selected_stations)
    
    def get_minuend_station_selected(self):
        selected = self.side_options.minuend_stations_list.selectedItems()
        if selected:
            return selected[0].text()
        return None

    def get_subtracted_station_selected(self):
        selected = self.side_options.subtracted_stations_list.selectedItems()
        if selected:
            return selected[0].text()
        return None

    def get_type_data(self):
        selected_types = list()
        if self.side_options.is_dH.isChecked(): selected_types.append('dH') 
        if self.side_options.is_H.isChecked(): selected_types.append('H')
        if self.side_options.is_dD.isChecked(): selected_types.append('dD')  
        if self.side_options.is_D.isChecked(): selected_types.append('D') 
        if self.side_options.is_dZ.isChecked(): selected_types.append('dZ') 
        if self.side_options.is_Z.isChecked(): selected_types.append('Z')
        if self.side_options.is_dI.isChecked(): selected_types.append('dI') 
        if self.side_options.is_I.isChecked(): selected_types.append('I') 
        if self.side_options.is_dF.isChecked(): selected_types.append('dF') 
        if self.side_options.is_F.isChecked(): selected_types.append('F') 
        if self.side_options.is_dG.isChecked(): selected_types.append('dG') 
        if self.side_options.is_G.isChecked(): selected_types.append('G') 
        if self.side_options.is_dX.isChecked(): selected_types.append('dX') 
        if self.side_options.is_X.isChecked(): selected_types.append('X') 
        if self.side_options.is_dY.isChecked(): selected_types.append('dY') 
        if self.side_options.is_Y.isChecked(): selected_types.append('Y') 
        if self.side_options.is_reference.isChecked(): selected_types.append('reference') 
        return selected_types

    def get_graph_type(self):
        return self.side_options.combo_type_plot.currentIndex()

    def get_date(self):
        return self.side_options.date.date().toPyDate()

    def get_start_date(self):
        #return self.side_options.startdate.date().toPyDate()
        return self.side_options.startdate.date()

    def get_end_date(self):
        return self.side_options.enddate.date().toPyDate()

    def get_column_entry(self):
        return int(self.side_options.columm_entry.currentText())
 
    def get_row_entry(self):
        return int(self.side_options.row_entry.currentText())
    
    def get_selected_dates(self):
        return self.side_options.selected_dates

    def get_cal_selection(self):
        return self.side_options.cal_calm

    def get_bold_text(self):
        return self.side_options.is_bold_text.isChecked()

    def get_grid_graph(self):
        return self.side_options.is_grid_graph.isChecked()