from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
from PIL import Image
from PIL import ImageQt
from General.util import Util
import os


class InitialPage(QWidget):
    def __init__(self, root, language):
        super().__init__(root)
        self.root = root
        self.lang = language
        self.util = Util()
    
    def pil_to_qimage(self, pil_image: Image.Image) -> QImage:
        pil_image = pil_image.convert("RGBA")
        data = pil_image.tobytes("raw", "RGBA")
        qimage = QImage(data, pil_image.width, pil_image.height, QImage.Format_RGBA8888)
        return qimage

    # cria página inicial
    def load_page(self):
        # remove widgets existentes
        self.util.destroy_existent_frames(self.root)

        # container principal
        initial_page_frame = QWidget(self.root)
        initial_page_frame.setStyleSheet("background-color: #212121;")
        layout = QVBoxLayout(initial_page_frame)
        layout.setAlignment(Qt.AlignCenter)
        width = self.root.width()
        height = self.root.height()

        # carregar imagem
        img = Image.open(self.util.resource_path("images/magnetic_field.png"))
        img_resized = img.resize((int(img.width * (width/2) / width),
                                  int(img.height * (height/2) / height)))
        qt_image = self.pil_to_qimage(img_resized)
        pixmap = QPixmap.fromImage(qt_image)

        lbl_image = QLabel()
        lbl_image.setPixmap(pixmap)
        lbl_image.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_image)
        layout.setContentsMargins(0, 30, 0, 30)

        # título
        lbl_title1 = QLabel('UMAGDA')
        lbl_title1.setStyleSheet("color: white; font-size: 30px; font-weight: bold;")
        lbl_title1.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_title1)

        lbl_title2 = QLabel('Univap Magnetometer Data Analysis')
        lbl_title2.setStyleSheet("color: white; font-size: 30px; font-weight: bold;")
        lbl_title2.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_title2)

        # define layout no frame
        initial_page_frame.setLayout(layout)

        # adiciona ao root
        self.root.setCentralWidget(initial_page_frame)
