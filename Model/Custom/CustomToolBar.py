from matplotlib.backends.backend_qt5 import NavigationToolbar2QT
from General.util import Util

# Função que remove pontos fora do zoom atual
def on_zoom_done(ax, tl):
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    # Remove anotações antigas
    for annotation in ax.texts:
        annotation.remove()
    # Adiciona anotações para coordenadas dentro do zoom
    for coord in tl or []:  # evita erro se tl for None
        if (xlim[0] <= coord['longitude'] <= xlim[1]) and (ylim[0] <= coord['latitude'] <= ylim[1]):
            ax.annotate(
                text=coord['station'],
                xy=(coord['longitude'], coord['latitude']),
                xytext=(5, 5),
                textcoords='offset points',
                ha='right',
            )
    ax.figure.canvas.draw_idle()  # Atualiza o canvas

class CustomToolbar(NavigationToolbar2QT):
    def __init__(self, canvas, parent=None, total_locals=None):
        super().__init__(canvas, parent)
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
        on_zoom_done(self.canvas.figure.gca(), self.total_locals)
