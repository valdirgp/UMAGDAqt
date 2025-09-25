from Model.GraphPage.GraphsModule import GraphsModule
from Model.GraphPage.SingleGraph import SingleGraph
from Model.GraphPage.GlobalGraph import GlobalGraph
from Model.GraphPage.ManyGraphs import ManyGraphs
from Model.GraphPage.TideGraph import TideGraph
from Model.GraphPage.DifferenceGraph import DifferenceGraph
from View.GraphPage import GraphPage

class GraphControl():
    def __init__(self, root, language, year, drive, magnetic_eq_coords=0):
        self.root = root
        self.lang = language
        self.year = year
        self.drive = drive
        self.Graphs = GraphPage(root, self.lang, self.year, self.drive, magnetic_eq_coords)
        self.Module = GraphsModule(self.lang)
        self.SingleModule = SingleGraph(self.root, self.lang)
        self.GlobalModule = GlobalGraph(self.root, self.lang)
        self.ManyModule = ManyGraphs(self.root, self.lang)
        self.TideModule = TideGraph(self.root, self.lang)
        self.DifferenceModule = DifferenceGraph(self.root, self.lang)
        

    # creates graph frames for the window and bind type of plots to variables
    def load_widgets(self):
        self.get_search_stations_downloaded()

        self.Graphs.bind_local_downloaded(lambda: self.get_search_stations_downloaded_filtred(self.Graphs.get_local_download()))
        self.Graphs.bind_single_graph(self.call_graph_creation)
        self.Graphs.bind_global_graph(self.call_graph_creation)
        self.Graphs.bind_many_graphs(self.call_graph_creation)

    # gets all the downloaded stations
    def get_search_stations_downloaded(self):
        downloaded_data_stations, self.data_with_stations = self.Module.search_stations_downloaded(self.year)
        self.Graphs.bind_search_stations_downloaded(downloaded_data_stations)
        #self.Graphs.bind_search_stations_downloaded(self.data_with_stations)
        self.Graphs.create_page_frames()

    # gets info and update downloaded data available
    def get_search_stations_downloaded_filtred(self, drive):
        downloaded_data_stations, self.data_with_stations = self.Module.search_stations_downloaded(self.year, drive)
        self.Graphs.bind_search_stations_downloaded(downloaded_data_stations)
        #self.Graphs.bind_search_stations_downloaded(self.data_with_stations)
        self.Graphs.update_data()

    # call graphs creation
    def call_graph_creation(self):
        match self.Graphs.get_graph_type():
            case 0: # SINGLE GRAPH
                if not self.Module.verify_inputs(station_selected=self.Graphs.get_stations_selected(), type_selected=self.Graphs.get_type_data()): return

                self.SingleModule.plot_day(
                    self.Graphs.get_local_download(),
                    self.Graphs.get_stations_selected(),
                    self.Graphs.get_type_data(),
                    self.Graphs.get_bold_text(),
                    self.Graphs.get_grid_graph(),
                    self.Graphs.get_date(),
                    self.Graphs.get_selected_dates(),
                    self.Graphs.get_cal_selection(),
                    self.data_with_stations,
                )
            case 1: # GLOBAL GRAPH
                if not self.Module.verify_inputs(station_selected=self.Graphs.get_stations_selected(), type_selected=self.Graphs.get_type_data()): return

                self.GlobalModule.plot_global_days(
                    self.Graphs.get_local_download(),
                    self.Graphs.get_stations_selected(),
                    self.Graphs.get_type_data(),
                    self.Graphs.get_bold_text(),
                    self.Graphs.get_grid_graph(),
                    self.Graphs.get_start_date(),
                    self.Graphs.get_end_date(),
                    self.Graphs.get_selected_dates(),
                    self.Graphs.get_cal_selection(),
                    self.data_with_stations,
                )
            case 2: # MANY GRAPHS
                if not self.Module.verify_inputs(station_selected=self.Graphs.get_stations_selected(), type_selected=self.Graphs.get_type_data()): return

                self.ManyModule.plot_more_days(
                    self.Graphs.get_local_download(),
                    self.Graphs.get_stations_selected(),
                    self.Graphs.get_type_data(),
                    self.Graphs.get_bold_text(),
                    self.Graphs.get_grid_graph(),
                    self.Graphs.get_start_date(),
                    self.Graphs.get_end_date(),
                    self.Graphs.get_selected_dates(),
                    self.Graphs.get_cal_selection(),
                    self.data_with_stations,
                    self.Graphs.get_column_entry(),
                    self.Graphs.get_row_entry(),
                )
            case 3: # TIDE'S GRAPH
                if not self.Module.verify_inputs(station_selected=self.Graphs.get_stations_selected(),type_selected=self.Graphs.get_type_data()): return

                self.TideModule.plot_tide(
                    self.Graphs.get_local_download(),
                    self.Graphs.get_stations_selected(),
                    self.Graphs.get_type_data(),
                    self.Graphs.get_bold_text(),
                    self.Graphs.get_grid_graph(),
                    self.Graphs.get_start_date(),
                    self.Graphs.get_end_date(),
                    self.Graphs.get_selected_dates(),
                    self.Graphs.get_cal_selection(),
                    self.data_with_stations,
                )
            
            case 4: # DIFFERENCE GRAPH
                if not self.Module.verify_inputs(type_selected=self.Graphs.get_type_data()): return

                self.DifferenceModule.plot_difference(
                    self.Graphs.get_local_download(),
                    self.Graphs.get_minuend_station_selected(),
                    self.Graphs.get_subtracted_station_selected(),
                    self.Graphs.get_type_data(),
                    self.Graphs.get_bold_text(),
                    self.Graphs.get_grid_graph(),
                    self.Graphs.get_start_date(),
                    self.Graphs.get_end_date(),
                    self.Graphs.get_selected_dates(),
                    self.Graphs.get_cal_selection(),
                    self.data_with_stations,
                )
    
    # expõe o widget para ser adicionado ao QStackedWidget
    def get_widget(self):
        return self.Graphs