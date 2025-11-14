from View.Frames.SideOptionsUniversalCD import SideOptionsUniversalCD
from View.Frames.Map import Map
from PyQt5.QtWidgets import QWidget, QHBoxLayout
from PyQt5.QtCore import QDate
import re
from General.util import Util
import cartopy.crs as ccrs
import numpy as np

class UniversalCDPage(QWidget):
    def __init__(self, root, language, year, final, drive, magnetic_eq_coords):
        super().__init__(root)
        self.root = root
        self.lang = language
        self.year = year
        self.final = final
        self.drive = drive
        self.magnetic_eq_coords = magnetic_eq_coords

        self.util = Util()
        self.side_options = SideOptionsUniversalCD(self, self.lang, self.year, self.final, self.drive)
        self.map_widget = Map(self)
        #SideOptionsUniversalCD.__init__(self, root, self.lang)
        #Map.__init__(self, root)

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

    
    def create_page_frames(self):
        if self.layout() is None:
            main_layout = QHBoxLayout(self)
            self.setLayout(main_layout)
        else:
            main_layout = self.layout()
                
        '''
        self.side_options.create_Ucalmdisturb_plot_options()
        self.get_downloaded_stations_location()
        self.side_options.populate_list_options(self.list_all_stations, self.downloaded_data_stations)
        self.side_options.list_all_stations.bind('<<ListboxSelect>>', self.listbox_on_click)
        '''
        # corrigido: usa o QListWidget que pertence a self.side_options e sinal do Qt
        self.side_options.create_Ucalmdisturb_plot_options()

        # preenche o QListWidget que está em self.side_options
        self.side_options.populate_list_options(self.side_options.list_all_stations, self.downloaded_data_stations)

        # conexão correta em PyQt5 (sem 'event' — itemSelectionChanged não entrega parâmetro)
        self.side_options.list_all_stations.itemSelectionChanged.connect(self.listbox_on_click)
        #self.side_options.btn_plot_selected.clicked.connect(self.bind_plot_selected)


        self.get_downloaded_stations_location()
        self.map_widget.create_map()
        self.colors = ['red'] * len(self.all_locals)
        self.map_widget.set_station_map(self.longitude, self.latitude)
        self.map_widget.set_stationsname_map(self.all_locals)
        
        longitudes = np.linspace(-180, 180, 361)

        y_values = self.ensure_array(self.magnetic_eq_coords, longitudes)
        self.map_widget.ax.plot(longitudes, y_values, color='red', lw='3', transform=ccrs.PlateCarree())
        self.map_widget.ax.plot(longitudes, y_values * 0, color='black', transform=ccrs.PlateCarree())

        self.map_widget.fig.canvas.mpl_connect('button_press_event', self.map_on_click)

        #main_layout.addWidget(self.frame_side_functions_ucalmdisturb)
        # adiciona o frame que foi criado dentro de self.side_options
        main_layout.addWidget(self.side_options.frame_side_functions_ucalmdisturb)

        main_layout.addWidget(self.map_widget.map_frame)


    '''
    def destroy_all_frames(self):
        # Destroy all existent frame in root
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.Frame):
                widget.destroy()
    '''


    def get_downloaded_stations_location(self):
        # Makes a list with all dictionary with station's name, longitude and latitude
        self.all_locals = []
        self.longitude = []
        self.latitude = []

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



    def listbox_on_click(self):
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
        

    def map_on_click(self, event):
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


    def can_be_number(self, number):
        # Checks if a string can be converted to a float
        try:
            number=float(number)
            return True
        except Exception:
            return False
        

    def update_data(self):
        self.side_options.populate_list_options(self.side_options.list_all_stations, self.downloaded_data_stations)
        
        self.map_widget.ax.callbacks.disconnect(self.map_widget.xlim_callback_id)
        self.map_widget.ax.callbacks.disconnect(self.map_widget.ylim_callback_id)

        for scatter in self.map_widget.scart_plots:
            scatter.remove()
        self.map_widget.scart_plots.clear()
        for text in self.map_widget.text_annotations:
            text.remove()
        self.map_widget.text_annotations.clear() 
        
        self.get_downloaded_stations_location()
        self.map_widget.set_station_map(self.longitude, self.latitude)
        self.map_widget.set_stationsname_map(self.all_locals)
        
        self.xlim_callback_id = self.map_widget.ax.callbacks.connect('xlim_changed', lambda ax: self.map_widget.update_annotations())
        self.ylim_callback_id = self.map_widget.ax.callbacks.connect('ylim_changed', lambda ax: self.map_widget.update_annotations())

        self.listbox_on_click()

        longitudes = np.linspace(-180, 180, 361)

        y_values = self.ensure_array(self.magnetic_eq_coords, longitudes)

        self.map_widget.ax.plot(longitudes, y_values, color='red', lw='3', transform=ccrs.PlateCarree())

        self.map_widget.canvas.draw()

        self.side_options.year = self.year
        self.side_options.final = self.final
        self.side_options.drive = self.drive

        #self.updateDrive()

        self.side_options.cal_calm.setSelectedDate(QDate(self.year[2], self.year[1], self.year[0]))
        self.side_options.cal_disturb.setSelectedDate(QDate(self.year[2], self.year[1], self.year[0]))
        self.side_options.startdate.setDate(QDate(self.year[2], self.year[1], self.year[0]))
        self.side_options.enddate.setDate(QDate(self.final[2], self.final[1], self.final[0]))

    def updateDrive(self, drive):
        self.side_options.combo_download_location.setCurrentText(drive)
    
    def updateMap(self):
        self.map_widget.ax.callbacks.disconnect(self.map_widget.xlim_callback_id)
        self.map_widget.ax.callbacks.disconnect(self.map_widget.ylim_callback_id)

        for scatter in self.map_widget.scart_plots:
            scatter.remove()
        self.map_widget.scart_plots.clear()
        for text in self.map_widget.text_annotations:
            text.remove()
        self.map_widget.text_annotations.clear() 
        
        self.get_downloaded_stations_location()
        self.map_widget.set_station_map(self.longitude, self.latitude)
        self.map_widget.set_stationsname_map(self.all_locals)
        
        self.xlim_callback_id = self.map_widget.ax.callbacks.connect('xlim_changed', lambda ax: self.map_widget.update_annotations())
        self.ylim_callback_id = self.map_widget.ax.callbacks.connect('ylim_changed', lambda ax: self.map_widget.update_annotations())

        self.listbox_on_click()

    def get_type_data(self):
        selected_types = list()
        if self.side_options.plot_checkboxes["H"].isChecked(): selected_types.append("H")
        if self.side_options.plot_checkboxes["X"].isChecked(): selected_types.append("X")
        if self.side_options.plot_checkboxes["Y"].isChecked(): selected_types.append("Y")
        if self.side_options.plot_checkboxes["Z"].isChecked(): selected_types.append("Z")
        if self.side_options.plot_checkboxes["D"].isChecked(): selected_types.append("D")
        if self.side_options.plot_checkboxes["F"].isChecked(): selected_types.append("F")
        if self.side_options.plot_checkboxes["I"].isChecked(): selected_types.append("I")
        if self.side_options.plot_checkboxes["G"].isChecked(): selected_types.append("G")
        return selected_types
        

    def bind_plot_selected(self, callback):
        self.side_options.btn_plot_selected.clicked.connect(callback)

    
    def bind_search_stations_downloaded(self, callback):
        self.downloaded_data_stations = callback


    def bind_local_downloaded(self, callback):
        self.local_downloads_function = callback

    '''def bind_updateMap(self, callback):
        self.side_options.updateMap_function = callback'''

    def get_start_date(self):
        return self.side_options.startdate.date()
    

    def get_end_date(self):
        return self.side_options.enddate.date()
    

    def get_selected_station(self):
        selected_stations = set()
        for i in range(self.side_options.list_all_stations.count()):
            item = self.side_options.list_all_stations.item(i)
            if item.isSelected():
                selected_stations.add(item.text().split()[0])
        return list(selected_stations)
    

    def get_selected_calm_dates(self):
        return self.side_options.selected_calm_dates
    

    def get_selected_disturb_dates(self):
        return self.side_options.selected_disturb_dates
    
    def get_local_download(self):
        return self.side_options.combo_download_location.currentText()