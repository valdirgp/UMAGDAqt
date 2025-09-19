from View.Frames.SideOptionsUniversalCD import SideOptionsUniversalCD
from View.Frames.Map import Map
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QMessageBox, QGridLayout
#import tkinter as tk
#import tkinter.messagebox as messagebox
#from tkinter import ttk
import re
from General.util import Util
import cartopy.crs as ccrs
import numpy as np

class UniversalCDPage(QWidget):
    def __init__(self, root, language, year, drive, magnetic_eq_coords):
        super().__init__(root)
        self.root = root
        self.lang = language
        self.year = year
        self.drive = drive
        self.magnetic_eq_coords = magnetic_eq_coords

        self.util = Util()
        self.side_options = SideOptionsUniversalCD(self, self.lang, self.year, self.drive)
        self.map_widget = Map(self)
        #SideOptionsUniversalCD.__init__(self, root, self.lang)
        #Map.__init__(self, root)

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
        # Creates frames for the tool
        #self.root.columnconfigure(0, weight=0)
        #self.root.columnconfigure(1, weight=1)
        #self.root.rowconfigure(0, weight=1)

        if self.layout() is None:
            main_layout = QHBoxLayout(self)
            self.setLayout(main_layout)
        else:
            main_layout = self.layout()
        
        #self.destroy_all_frames()
        
        '''
        self.side_options.create_Ucalmdisturb_plot_options()
        self.get_downloaded_stations_location()
        self.side_options.populate_list_options(self.list_all_stations, self.downloaded_data_stations)
        self.side_options.list_all_stations.bind('<<ListboxSelect>>', self.listbox_on_click)
        '''
        # corrigido: usa o QListWidget que pertence a self.side_options e sinal do Qt
        self.side_options.create_Ucalmdisturb_plot_options()
        self.get_downloaded_stations_location()

        # preenche o QListWidget que está em self.side_options
        self.side_options.populate_list_options(self.side_options.list_all_stations, self.downloaded_data_stations)

        # conexão correta em PyQt5 (sem 'event' — itemSelectionChanged não entrega parâmetro)
        self.side_options.list_all_stations.itemSelectionChanged.connect(self.listbox_on_click)

        #self.side_options.btn_plot_selected.clicked.connect(self.bind_plot_selected)


        self.map_widget.create_map()
        self.colors = ['red'] * len(self.all_locals)
        self.map_widget.set_station_map(self.longitude, self.latitude)
        self.map_widget.set_stationsname_map(self.all_locals)
        
        longitudes = np.linspace(-180, 180, 361)

        y_values = self.ensure_array(self.magnetic_eq_coords, longitudes)
        self.map_widget.ax.plot(longitudes, y_values, color='gray', transform=ccrs.PlateCarree())
        self.map_widget.ax.plot(longitudes, y_values * 0, color='gray', transform=ccrs.PlateCarree())

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

        try:
            with open('readme_stations.txt','r') as file: 
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
            #self.lbl_warning_message = ttk.Label(master=self.frame_side_functions_calmdisturb.inner_frame, text=self.util.dict_language[self.lang]['lbl_noreadme']).grid(row=17, column=0, columnspan=2)
            # tenta primeiro no objeto side_options (onde os widgets foram criados)
            frame = getattr(self.side_options, 'frame_side_functions_ucalmdisturb', None)
            # fallback: se por algum motivo o frame estiver em self
            if frame is None:
                frame = getattr(self, 'frame_side_functions_ucalmdisturb', None)

            if frame is None:
                # Nenhum lugar óbvio para anexar o label — coloca no self como fallback
                self.lbl_warning_message = QLabel(self.util.dict_language[self.lang]['lbl_noreadme'], self)
                # opcional: se você tiver um layout principal, adicione lá
                # main_layout.addWidget(self.lbl_warning_message)
            else:
                # garante que exista um QGridLayout no inner_frame
                if not hasattr(frame, 'inner_layout') or frame.inner_layout is None:
                    frame.inner_layout = QGridLayout(frame.inner_frame)
                    frame.inner_frame.setLayout(frame.inner_layout)

                self.lbl_warning_message = QLabel(self.util.dict_language[self.lang]['lbl_noreadme'], frame.inner_frame)
                # (row=17, col=0, rowspan=1, colspan=2) equivalente ao columnspan=2 do Tk
                frame.inner_layout.addWidget(self.lbl_warning_message, 17, 0, 1, 2)


    def listbox_on_click(self):
        # Change map's status when listbox is selected
        items_from_list = [self.side_options.list_all_stations.item(i).text() for i in range(self.side_options.list_all_stations.count())]
        '''for i, local in enumerate(self.all_locals):
            selection = itens_from_list.index(local['station'])
            if self.colors[i] == 'red' and selection in event.widget.curselection():
                self.colors[i] = 'lightgreen'
            elif self.colors[i] == 'lightgreen' and selection not in event.widget.curselection():
                self.colors[i] = 'red'

        self.scart.set_facecolors(self.colors)
        self.canvas.draw()'''
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
        


    def map_on_click(self, event):
        # Change map's status and listbox's status when map's button is selected
        '''if event.inaxes is not None:
            selected_longitude, selected_latitude = event.xdata, event.ydata

            for i, local in enumerate(self.all_locals):
                if abs(selected_longitude - local['longitude']) < 1.0 and abs(selected_latitude - local['latitude']) < 1.0:
                    itens_from_list = self.list_all_stations.get(0, tk.END)
                    selection = itens_from_list.index(local['station'])
                    if self.colors[i] == 'red':
                        self.list_all_stations.selection_set(selection)
                        self.colors[i] = 'lightgreen'
                    else: 
                        self.list_all_stations.selection_clear(selection)
                        self.colors[i] = 'red'

                    self.scart.set_facecolors(self.colors)
                    self.canvas.draw()'''
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


    def can_be_number(self, number):
        # Checks if a string can be converted to a float
        try:
            number=float(number)
            return True
        except Exception:
            return False
        

    def update_data(self):
        self.side_options.list_all_stations.clear()
        self.side_options.populate_list_options(self.side_options.list_all_stations, self.downloaded_data_stations)
        for scatter in self.scart_plots:
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


    def get_start_date(self):
        return self.side_options.startdate.date()
    

    def get_end_date(self):
        return self.side_options.enddate.date()
    

    def get_selected_station(self):
        selected_stations = set()
        for i in range(self.side_options.list_all_stations.count()):
            item = self.side_options.list_all_stations.item(i)
            if item.isSelected():
                selected_stations.add(item.text())
        return list(selected_stations)
    

    def get_selected_calm_dates(self):
        return self.side_options.selected_calm_dates
    

    def get_selected_disturb_dates(self):
        return self.side_options.cal_disturb
    
    def get_local_download(self):
        return self.side_options.combo_download_location.currentText()