from View.CalmPage import CalmPage
from Model.GraphPage.GraphsModule import GraphsModule
from Model.CalmPage.CalmGraphs import CalmModel

class CalmControl():
    def __init__(self, root, language, magnetic_eq_coords=0):
        self.root = root
        self.lang = language
        self.Graphs = CalmPage(root, self.lang, magnetic_eq_coords)
        self.Model = GraphsModule(self.lang)
        self.CModel = CalmModel(self.root, self.lang)

    # Creates graph frames for the window and binds plot functions to buttons
    def load_widgets(self):
        self.get_search_stations_downloaded()
        self.Graphs.create_page_frames()

        self.Graphs.bind_local_downloaded(lambda: self.get_search_stations_downloaded_filtred(
                                        self.Graphs.get_local_download()
                                        ))

        # Bind the plot function to the confirm button using the correct callback setup
        self.Graphs.bind_plot_graph_H(lambda: self.CModel.create_graphics_calm(
                                    self.Graphs.get_local_download(),
                                    self.Graphs.get_start_date(),
                                    self.Graphs.get_end_date(),
                                    self.Graphs.get_selected_station(),
                                    self.data_with_stations,
                                    self.Graphs.get_selected_calm_dates(),
                                    "H"
                                    ))
        
        self.Graphs.bind_plot_graph_Z(lambda: self.CModel.create_graphics_calm(
                                    self.Graphs.get_local_download(),
                                    self.Graphs.get_start_date(),
                                    self.Graphs.get_end_date(),
                                    self.Graphs.get_selected_station(),
                                    self.data_with_stations,
                                    self.Graphs.get_selected_calm_dates(),
                                    "Z"
                                    ))

    # Gets all the downloaded stations
    def get_search_stations_downloaded(self):
        downloaded_data_stations, self.data_with_stations = self.Model.search_stations_downloaded()
        self.Graphs.bind_search_stations_downloaded(downloaded_data_stations)

    
    def get_search_stations_downloaded_filtred(self, drive):
        downloaded_data_stations, self.data_with_stations = self.Model.search_stations_downloaded(drive)
        self.Graphs.bind_search_stations_downloaded(downloaded_data_stations)
        self.Graphs.update_data()

        

    def get_widget(self):
        return self.Graphs
