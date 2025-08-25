from Model.DownloadPage.DownloadsModule import DownloadModule
from Model.DownloadPage.Embrace import Embrace
from Model.DownloadPage.Intermagnet import Intermagnet
from Model.DownloadPage.Readme import Readme
from View.DownloadPage import DownloadPage

class DownloadsControl():
    def __init__(self, root, language, magnetic_eq_coords=0):
        self.root = root
        self.lang = language
        self.DownloadPage = DownloadPage(self.root, self.lang, magnetic_eq_coords)
        self.Module = DownloadModule(self.lang)
        self.Embrace = Embrace(self.lang)
        self.Intermagnet = Intermagnet(self.lang)
        self.Readme = Readme(self.lang)

        self.embrace_stations = self.Embrace.create_stationlist()
        self.intermagnet_stations = self.Intermagnet.create_stationlist()

    # creates page and bind its buttons
    def load_widgets(self):
        self.DownloadPage.set_embrace_options(self.embrace_stations)
        self.DownloadPage.set_intermagnet_options(self.intermagnet_stations)
        self.config_page()

    # set page features
    def config_page(self):
        self.DownloadPage.create_page_frames()
        self.DownloadPage.bind_download(self.call_both)
        self.DownloadPage.bind_download_readme(self.create_readme_file)

    # gets all stations in a file with their info
    def create_readme_file(self):
        self.Readme.createfile_readme(self.DownloadPage.get_options_frame(), self.embrace_stations, self.intermagnet_stations, self.config_page)

    # call downloaders from embrace and intermagnet network
    def call_both(self):
        if not self.Module.verify_inputs(self.DownloadPage.get_stations_selected(), 
                                         self.DownloadPage.get_duration_chosen(), 
                                         self.DownloadPage.get_duration_type()):
            return
        
        if any(item in self.embrace_stations for item in self.DownloadPage.get_stations_selected()):
            self.Embrace.initialize_download_Embrace(self.DownloadPage.get_options_frame(),
                                            self.DownloadPage.get_local_download(),
                                            self.DownloadPage.get_stations_selected(),
                                            self.DownloadPage.get_duration_chosen(),
                                            self.DownloadPage.get_duration_type(),
                                            self.DownloadPage.get_date())

        if any(item in self.intermagnet_stations for item in self.DownloadPage.get_stations_selected()):
            self.Intermagnet.initialize_download_Intermagnet(self.DownloadPage.get_options_frame(),
                                                    self.DownloadPage.get_local_download(),
                                                    self.DownloadPage.get_stations_selected(),
                                                    self.DownloadPage.get_duration_chosen(), 
                                                    self.DownloadPage.get_duration_type(),
                                                    self.DownloadPage.get_date())