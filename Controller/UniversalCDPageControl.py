from Model.GraphPage.GraphsModule import GraphsModule
from Model.UniversalCDPage.UniversalCDGraphs import UniversalCDModel
from View.UniversalCDPage import UniversalCDPage

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
        for dtype in selected_types:
            match dtype:
                case "H":
                    self.CDModel.create_graphics_calm_distU_H(
                        self.Graphs.get_local_download(),
                        self.Graphs.get_start_date(),
                        self.Graphs.get_end_date(),
                        self.Graphs.get_selected_station(),
                        self.data_with_stations,
                        self.Graphs.get_selected_calm_dates(),
                        self.Graphs.get_selected_disturb_dates()
                    )
                case "X":
                    self.CDModel.create_graphics_calm_distU_X(
                        self.Graphs.get_local_download(),
                        self.Graphs.get_start_date(),
                        self.Graphs.get_end_date(),
                        self.Graphs.get_selected_station(),
                        self.data_with_stations,
                        self.Graphs.get_selected_calm_dates(),
                        self.Graphs.get_selected_disturb_dates()
                    )
                case "Y":
                    self.CDModel.create_graphics_calm_distU_Y(
                        self.Graphs.get_local_download(),
                        self.Graphs.get_start_date(),
                        self.Graphs.get_end_date(),
                        self.Graphs.get_selected_station(),
                        self.data_with_stations,
                        self.Graphs.get_selected_calm_dates(),
                        self.Graphs.get_selected_disturb_dates()
                    )
                case "Z":
                    self.CDModel.create_graphics_calm_distU_Z(
                        self.Graphs.get_local_download(),
                        self.Graphs.get_start_date(),
                        self.Graphs.get_end_date(),
                        self.Graphs.get_selected_station(),
                        self.data_with_stations,
                        self.Graphs.get_selected_calm_dates(),
                        self.Graphs.get_selected_disturb_dates()
                    )
                case "D":
                    self.CDModel.create_graphics_calm_distU_D(
                        self.Graphs.get_local_download(),
                        self.Graphs.get_start_date(),
                        self.Graphs.get_end_date(),
                        self.Graphs.get_selected_station(),
                        self.data_with_stations,
                        self.Graphs.get_selected_calm_dates(),
                        self.Graphs.get_selected_disturb_dates()
                        )
                case "F":
                    self.CDModel.create_graphics_calm_distU_F(
                        self.Graphs.get_local_download(),
                        self.Graphs.get_start_date(),
                        self.Graphs.get_end_date(),
                        self.Graphs.get_selected_station(),
                        self.data_with_stations,
                        self.Graphs.get_selected_calm_dates(),
                        self.Graphs.get_selected_disturb_dates()
                        )
                case "I":
                    self.CDModel.create_graphics_calm_distU_I(
                        self.Graphs.get_local_download(),
                        self.Graphs.get_start_date(),
                        self.Graphs.get_end_date(),
                        self.Graphs.get_selected_station(),
                        self.data_with_stations,
                        self.Graphs.get_selected_calm_dates(),
                        self.Graphs.get_selected_disturb_dates()
                        )
                case "G":
                    self.CDModel.create_graphics_calm_distU_G(
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
        downloaded_data_stations, self.data_with_stations = self.Model.search_stations_downloaded(self.year, drive)
        self.Graphs.bind_search_stations_downloaded(downloaded_data_stations)
        self.Graphs.update_data()

    def get_widget(self):
        return self.Graphs
