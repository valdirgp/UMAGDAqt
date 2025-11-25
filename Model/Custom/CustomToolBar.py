from matplotlib.backends.backend_qt5 import NavigationToolbar2QT
from General.util import Util
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction

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
    
    def __init__(self, canvas, window, map_instance=None):
        super().__init__(canvas, window)
        self.util = Util()
        self.map_instance = map_instance

        self.bindFavoritar()   
        self.bindContorno()     

    def bindFavoritar(self):
        icon = QIcon(self.util.resource_pathGeneral('images/favoritar.ico'))   # caminho do ícone
        self.save_zoom_action = QAction(icon, "Salvar Zoom", self)
        self.save_zoom_action.triggered.connect(self.save_zoom_clicked)

        # insere ao final da barra
        save_action = self.actions()[-1]  # O penúltimo é o botão "SALVAR" padrão
        self.insertAction(save_action, self.save_zoom_action)
    
    def bindContorno(self):
        icon = QIcon(self.util.resource_pathGeneral('images/globo.ico'))
        self.mapa_contorno_action = QAction(icon, "Mapa Contorno", self)
        self.mapa_contorno_action.triggered.connect(self.mapa_contorno)
        save_action = self.actions()[-1]
        self.insertAction(save_action, self.mapa_contorno_action)


    def home(self):
        super().home()
        if self.map_instance:
            self.map_instance.update_annotations()

    def release_zoom(self, event):
        super().release_zoom(event)
        if self.map_instance:
            self.map_instance.update_annotations()

    def back(self):
        super().back()
        if self.map_instance:
            self.map_instance.update_annotations()

    def forward(self):
        super().forward()
        if self.map_instance:
            self.map_instance.update_annotations()
    
    def save_zoom_clicked(self):
        if self.map_instance:
            self.map_instance.save_current_zoom()
    
    def mapa_contorno(self):
        if self.map_instance:
            self.map_instance.mapa_contorno()