from Model.GraphPage.GraphsModule import GraphsModule
from Model.CalmDisturbPage.CalmDisturbGraphs import CalmDisturbModel
from View.CalmDisturbPage import CalmDisturbPage


class CalmDisturbControl:
    def __init__(self, root, language, year, drive, magnetic_eq_coords=0):
        self.root = root
        self.lang = language
        self.year = year
        self.drive = drive
        self.Graphs = CalmDisturbPage(root, self.lang, self.year, self.drive, magnetic_eq_coords)
        self.Model = GraphsModule(self.lang)
        self.CDModel = CalmDisturbModel(self.root, self.lang)

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

        # callback do botão confirmar (gera os gráficos)
        self.Graphs.bind_plot_graph(
            lambda: self.CDModel.create_graphics_calm_dist(
                self.Graphs.get_local_download(),
                self.Graphs.get_start_date(),
                self.Graphs.get_end_date(),
                self.Graphs.get_selected_station(),
                self.data_with_stations,
                self.Graphs.get_selected_calm_dates(),
                self.Graphs.get_selected_disturb_dates(),
            )
        )

    # busca todas as estações baixadas
    def get_search_stations_downloaded(self):
        downloaded_data_stations, self.data_with_stations = self.Model.search_stations_downloaded()
        self.Graphs.bind_search_stations_downloaded(downloaded_data_stations)

    # busca estações filtrando pelo drive selecionado
    def get_search_stations_downloaded_filtred(self, drive):
        downloaded_data_stations, self.data_with_stations = self.Model.search_stations_downloaded(drive)
        self.Graphs.bind_search_stations_downloaded(downloaded_data_stations)
        self.Graphs.update_data()


    def get_widget(self):
        return self.Graphs