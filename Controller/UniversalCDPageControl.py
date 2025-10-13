from Model.GraphPage.GraphsModule import GraphsModule
from Model.UniversalCDPage.UniversalCDGraphs import UniversalCDModel
from View.UniversalCDPage import UniversalCDPage
from PyQt5.QtCore import QFileSystemWatcher
from General.util import Util
import sys, os

class UniversalCDPageControl():
    def __init__(self, root, language, year, final, drive, magnetic_eq_coords=0):
        self.root = root
        self.lang = language
        self.year = year
        self.final = final
        self.drive = drive
        self.Graphs = UniversalCDPage(root, self.lang, self.year, self.final, self.drive, magnetic_eq_coords)
        self.Model = GraphsModule(self.lang)
        self.CDModel = UniversalCDModel(self.root, self.lang)

        self.watcher = QFileSystemWatcher()
        self.util = Util()

        path = self.resource_path("config.txt")
        self.watcher.addPath(path)
        #self.watcher.fileChanged.connect(self.update_listbox_on_change)
        self.watcher.fileChanged.connect(lambda: self.get_search_stations_downloaded_filtred(self.drive))

    # creates an absolute path
    @staticmethod
    def resource_path(relative_path):
        try:
            base_path = sys._MEIPASS
            base_path = os.path.join(base_path, "General")
        except Exception:
            base_path = os.path.abspath("./General")
            
        return os.path.join(base_path, relative_path)

    # Creates graph frames for the window and binds plot functions to buttons
    def load_widgets(self):
        self.get_search_stations_downloaded()
        self.config_page()
        
    
    def config_page(self):
        self.Graphs.create_page_frames()

        self.Graphs.bind_local_downloaded(lambda: self.get_search_stations_downloaded_filtred(
                                        self.Graphs.get_local_download()
                                        ))

        self.Graphs.bind_plot_selected(self.plot_selected)

    def plot_selected(self):
        selected_types = [dtype for dtype in self.Graphs.get_type_data() if dtype is not None or ""]
        self.selected_station = self.Graphs.get_selected_station()
        self.calm_date = self.Graphs.get_selected_calm_dates()
        self.disturb_date = self.Graphs.get_selected_disturb_dates()
        if not self.Model.verify_inputs(
            station_selected= self.selected_station,
            type_selected= selected_types,
            calm_dates_selected= self.calm_date,
            disturb_dates_selected= self.disturb_date
        ): return
        for dtype in selected_types:

            self.CDModel.create_graphics_calm_distU(
                dtype,  # componente (H, X, Y, Z, D, F, I, G)
                self.Graphs.get_local_download(),
                self.Graphs.get_start_date(),
                self.Graphs.get_end_date(),
                self.Graphs.get_selected_station(),
                self.data_with_stations,
                self.Graphs.get_selected_calm_dates(),
                self.Graphs.get_selected_disturb_dates()
            )

    # gets all the downloaded stations
    def get_search_stations_downloaded(self):
        downloaded_data_stations, self.data_with_stations = self.Model.search_stations_downloaded(self.year)
        self.Graphs.bind_search_stations_downloaded(downloaded_data_stations)

    
    def get_search_stations_downloaded_filtred(self, drive):
        if self.util.get_year_config() != self.year:
            self.year = self.util.get_year_config()
        if self.util.get_final_config() != self.final:
            self.final = self.util.get_final_config()
        downloaded_data_stations, self.data_with_stations = self.Model.search_stations_downloaded(self.year, drive)
        self.Graphs.bind_search_stations_downloaded(downloaded_data_stations)
        self.Graphs.year = self.year
        self.Graphs.final = self.final
        self.Graphs.update_data()

    def get_widget(self):
        return self.Graphs
