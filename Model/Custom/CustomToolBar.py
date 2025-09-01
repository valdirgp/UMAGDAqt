from matplotlib.backends.backend_qt5 import NavigationToolbar2QT
from General.util import Util

# function that removes points outside of the zoomed map
def on_zoom_done(ax, tl):
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    for annotation in ax.texts:
        annotation.remove()
    for coord in tl:
        if coord['longitude'] >= xlim[0] and coord['longitude'] <= xlim[1] and coord['latitude'] >= ylim[0] and coord['latitude'] <= ylim[1]:
            ax.annotate(
                text=coord['station'],
                xy=(coord['longitude'], coord['latitude']),
                xytext=(5, 5),
                textcoords='offset points',
                ha='right',
            )

class CustomToolbar(NavigationToolbar2QT):
    def __init__(self, canvas, window, total_locals=None):
        super().__init__(canvas, window)
        self.total_locals = total_locals
        self.util = Util()

    def home(self):
        super().home()
        on_zoom_done(self.canvas.figure.gca(), self.total_locals)

    def release_zoom(self, event):
        super().release_zoom(event)
        on_zoom_done(self.canvas.figure.gca(), self.total_locals)

    def back(self):
        super().back()
        on_zoom_done(self.canvas.figure.gca(), self.total_locals)

    def forward(self):
        super().forward()