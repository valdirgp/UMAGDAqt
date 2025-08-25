from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from PIL import Image
from General.util import Util

class InitialPage:
    def __init__(self, root: QWidget, language):
        self.root = root
        self.lang = language
        self.util = Util()

    def load_page(self):
        self.util.destroy_existent_frames(self.root)  # Essa função deve ser adaptada também para PyQt5

        # Cria um widget central e define layout vertical
        initial_page_widget = QWidget(self.root)
        initial_page_widget.setStyleSheet("background-color: #212121;")
        layout = QVBoxLayout(initial_page_widget)
        layout.setAlignment(Qt.AlignCenter)

        # Tamanhos da tela
        screen_geometry = self.root.screen().geometry()
        width = screen_geometry.width()
        height = screen_geometry.height()

        # Carrega imagem
        img = Image.open(self.util.resource_path("images/magnetic_field.png"))
        img_resized = img.resize((int(img.width * (width/2) / width), int(img.height * (height/2) / height)))
        qt_image = QPixmap(img_resized.filename)  # QPixmap aceita caminho de arquivo direto

        lbl_image = QLabel()
        lbl_image.setPixmap(qt_image)
        lbl_image.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_image)

        # Título principal
        title_label = QLabel('UMAGDA')
        title_label.setStyleSheet("color: white; font-size: 30pt; font-weight: bold;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # Subtítulo
        subtitle_label = QLabel('Univap Magnetometer Data Analysis')
        subtitle_label.setStyleSheet("color: white; font-size: 30pt; font-weight: bold;")
        subtitle_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle_label)

        # Adiciona a página ao widget principal
        self.root.setCentralWidget(initial_page_widget)
