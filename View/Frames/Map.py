from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from Model.Custom.CustomToolBar import CustomToolbar
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt

class Map(QWidget):
    def __init__(self, root):
        super().__init__(root)
        self.page_frame = root
        self.colors = None
        self.map_frame = None
        self.toolbar = None
        self.canvas = None

        self.scart_plots = []
        self.text_annotations = []
        self.all_locals = []

    # creates frame for to select stations
    def create_map(self):
        # Main layout for the map frame
        self.map_frame = QWidget(self.page_frame)
        layout = QVBoxLayout(self.map_frame)
        #self.map_frame.setLayout(layout)
        '''if self.map_frame.layout() is None:
            layout = QVBoxLayout(self)
            self.setLayout(main_layout)
        else:
            main_layout = self.layout()  # usa o layout já existente'''


        # Create matplotlib figure and axis with Cartopy
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(projection=ccrs.PlateCarree())
        self.fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
        for spine in self.ax.spines.values():
            spine.set_linewidth(2)

        self.ax.add_feature(cfeature.LAND)
        self.ax.add_feature(cfeature.OCEAN)
        self.ax.add_feature(cfeature.COASTLINE)
        self.ax.add_feature(cfeature.BORDERS)
        self.ax.add_feature(cfeature.RIVERS)

        # Create the canvas and toolbar for PyQt5
        self.canvas = FigureCanvas(self.fig)
        self.toolbar = CustomToolbar(self.canvas, self.map_frame, total_locals=self.all_locals)

        # Add toolbar and canvas to the layout
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

        self.map_frame.setLayout(layout)
        self.map_frame.show()

    # creates points in the map accordingly to longitude and latitude list
    def set_station_map(self, longitude, latitude):
        current_extent = self.ax.get_extent()
        self.colors = ['red'] * len(longitude)
        self.scart = self.ax.scatter(longitude, latitude, s=50, c=self.colors, marker='8', transform=ccrs.PlateCarree())
        self.ax.set_extent(current_extent, crs=ccrs.PlateCarree())
        self.scart_plots.append(self.scart)
        self.canvas.draw()

    # creates text in given coordinates in station_locals and its name
    def set_stationsname_map(self, station_locals):
        for coord in station_locals:
            text = self.ax.annotate(
                text=coord['station'],
                xy=(coord['longitude'], coord['latitude']),
                xytext=(5, 5),
                textcoords='offset points',
                ha='right'
            )
            self.text_annotations.append(text)
        self.canvas.draw()

    # select all points from map
    def select_all_points(self):
        self.colors = ['lightgreen'] * len(self.all_locals)
        self.scart.set_facecolors(self.colors)
        self.canvas.draw()

    # clear all points from map
    def clear_all_points(self):
        self.colors = ['red'] * len(self.all_locals)
        self.scart.set_facecolor(self.colors)
        self.canvas.draw()