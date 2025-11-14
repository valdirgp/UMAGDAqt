from Model.GraphPage.GraphsModule import GraphsModule
from Model.CalmDisturbPage.CalmDisturbGraphs import CalmDisturbModel
from View.CalmDisturbPage import CalmDisturbPage
from PyQt5.QtCore import QFileSystemWatcher
from General.util import Util
import sys, os

class CalmDisturbControl:
    def __init__(self, root, language, year, final, drive, magnetic_eq_coords=0):
        self.root = root
        self.lang = language
        self.year = year
        self.final = final
        self.drive = drive
        self.Graphs = CalmDisturbPage(root, self.lang, self.year, self.final, self.drive, magnetic_eq_coords)
        self.Model = GraphsModule(self.lang)
        self.CDModel = CalmDisturbModel(self.root, self.lang)

        self.watcher = QFileSystemWatcher()
        self.util = Util()

        path = self.resource_path("config.txt")
        self.watcher.addPath(path)
        #self.watcher.fileChanged.connect(self.update_listbox_on_change)
        self.watcher.fileChanged.connect(lambda: self.get_search_stations_downloaded_filtred(self.util.get_drive_config()))

    # creates an absolute path
    @staticmethod
    def resource_path(relative_path):
        try:
            base_path = sys._MEIPASS
            base_path = os.path.join(base_path, "General")
        except Exception:
            base_path = os.path.abspath("./General")
            
        return os.path.join(base_path, relative_path)

    # Cria os frames e conecta os callbacks
    def load_widgets(self):
        self.get_search_stations_downloaded()
        self.Graphs.create_page_frames()

        # callback quando mudar local de download
        self.Graphs.bind_local_downloaded(
            lambda: self.get_search_stations_downloaded_filtred(
                self.Graphs.get_local_download()
            )
        )

        #self.Graphs.bind_updateMap(lambda: self.Graphs.updateMap())

        # callback do botão confirmar (gera os gráficos)
        self.Graphs.bind_plot_graph(self.tryna_plot)

    
    def tryna_plot(self):
        self.station_selected = self.Graphs.get_selected_station()
        self.calm_date = self.Graphs.get_selected_calm_dates()
        self.disturb_date = self.Graphs.get_selected_disturb_dates()

        if not self.Model.verify_inputs(
            station_selected= self.station_selected,
            calm_dates_selected= self.calm_date,
            disturb_dates_selected= self.disturb_date
        ): return

        self.CDModel.create_graphics_calm_dist(
            self.Graphs.get_local_download(),
            self.Graphs.get_start_date(),
            self.Graphs.get_end_date(),
            self.Graphs.get_selected_station(),
            self.data_with_stations,
            self.Graphs.get_selected_calm_dates(),
            self.Graphs.get_selected_disturb_dates(),
        )

    # busca todas as estações baixadas
    def get_search_stations_downloaded(self):
        downloaded_data_stations, self.data_with_stations = self.Model.search_stations_downloaded(self.year, self.drive)
        self.Graphs.bind_search_stations_downloaded(downloaded_data_stations)

    # busca estações filtrando pelo drive selecionado
    def get_search_stations_downloaded_filtred(self, drive):
        if self.util.get_year_config() != self.year:
            self.year = self.util.get_year_config()
        if self.util.get_final_config() != self.final:
            self.final = self.util.get_final_config()
        
        self.drive = self.util.get_drive_config()
        downloaded_data_stations, self.data_with_stations = self.Model.search_stations_downloaded(self.year, drive)
        self.Graphs.bind_search_stations_downloaded(downloaded_data_stations)
        self.Graphs.year = self.year
        self.Graphs.final = self.final
        self.Graphs.drive = self.drive
        if self.Graphs.side_options.combo_download_location.currentText() != self.util.get_drive_config():
            self.Graphs.updateDrive(self.util.get_drive_config())
        self.Graphs.update_data()

    def get_widget(self):
        return self.Graphs