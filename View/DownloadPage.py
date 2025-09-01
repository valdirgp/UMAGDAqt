from View.Frames.SideOptionsDownload import SideOptionsDownload
from View.Frames.Map import Map
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel
import re
from General.util import Util
import cartopy.crs as ccrs
import numpy as np

class DownloadPage(QWidget):
    def __init__(self, root, language, magnetic_eq_coords):
        super().__init__(root)
        self.root = root
        self.lang = language
        self.magnetic_eq_coords = magnetic_eq_coords

        self.selected_listbox = []
        self.all_locals = []
        self.colors = []

        self.util = Util()
        self.side_options = SideOptionsDownload(root, self.lang)
        self.map_widget = Map(root)
        self.embrace_stations = []
        self.intermagnet_stations = []

    # creates frames for the tool
    def create_page_frames(self):
        # Layout principal horizontal
        main_layout = QHBoxLayout(self.root)
        self.root.setLayout(main_layout)

        self.util.destroy_existent_frames(self.root)

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
        self.map_widget.set_station_map(self.longitude, self.latitude)
        self.map_widget.set_stationsname_map(self.all_locals)

        longitudes = np.linspace(-180, 180, 361)
        self.map_widget.ax.plot(longitudes, self.magnetic_eq_coords, color='gray', transform=ccrs.PlateCarree())

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

        try:
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
        except Exception:
            warning = QLabel(self.util.dict_language[self.lang]['lbl_noreadme'])
            self.side_options.options_frame.inner_frame.layout().addWidget(warning)

    # change map's status when listbox is selected
    def listbox_on_click(self):
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

    # change map's status and listbox's status when map's button is selected
    def map_on_click(self, event):
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
                selected_stations.add(item.text())
        return list(selected_stations)

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