from PyQt5.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from Model.Custom.CustomToolBar import CustomToolbar
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt

class Map(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.all_locals = []
        self.colors = []
        self.scart_plots = []
        self.text_annotations = []

        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)
        self.create_map()

    def create_map(self):
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

        self.canvas = FigureCanvas(self.fig)
        self.layout.addWidget(self.canvas)

        self.toolbar = CustomToolbar(self.canvas, self, total_locals=self.all_locals)
        self.layout.addWidget(self.toolbar)
        self.canvas.draw()

    def set_station_map(self, longitude, latitude):
        current_extent = self.ax.get_extent()
        self.colors = ['red'] * len(longitude)
        self.scart = self.ax.scatter(longitude, latitude, s=50, c=self.colors, marker='8', transform=ccrs.PlateCarree())
        self.ax.set_extent(current_extent, crs=ccrs.PlateCarree())
        self.scart_plots.append(self.scart)
        self.canvas.draw()

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

    def select_all_points(self):
        if self.colors:
            self.colors = ['lightgreen'] * len(self.all_locals)
            self.scart.set_facecolors(self.colors)
            self.canvas.draw()

    def clear_all_points(self):
        if self.colors:
            self.colors = ['red'] * len(self.all_locals)
            self.scart.set_facecolors(self.colors)
            self.canvas.draw()
