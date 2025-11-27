from PyQt5.QtWidgets import QSplashScreen, QLabel
from PyQt5.QtGui import QMovie, QPixmap
from PyQt5.QtCore import Qt
from General.util import Util

class LoadingScreen(QSplashScreen):
    def __init__(self):
        super().__init__(QPixmap(400, 300))  # tamanho base
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        self.label = QLabel(self)
        self.label.setGeometry(0, 0, 500, 400)
        self.label.setAlignment(Qt.AlignCenter)

        self.movie = QMovie(Util.resource_pathGeneral('images/loading.gif'))
        self.label.setMovie(self.movie)
        self.movie.start()
