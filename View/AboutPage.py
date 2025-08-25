from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt
from General.util import Util

class AboutPage:
    def __init__(self, root, language):
        self.root = root
        self.lang = language
        self.util = Util()

    def load_page(self):
        self.util.destroy_existent_frames(self.root)

        about_widget = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        about_widget.setLayout(layout)

        # Desenvolvedores
        dev_title = QLabel(f"{self.util.dict_language[self.lang]['lbl_dev']}:")
        dev_title.setStyleSheet("font-size: 20pt; font-weight: bold;")
        layout.addWidget(dev_title)

        dev1 = QLabel("Leonardo Ribeiro da Silva Faria")
        dev1.setStyleSheet("font-size: 12pt;")
        layout.addWidget(dev1)

        dev2 = QLabel("Thiago Alexander Moreira Mancilla")
        dev2.setStyleSheet("font-size: 12pt; margin-bottom: 10px;")
        
        layout.addWidget(dev2)

        dev3 = QLabel("Valdir Gill Pillat")
        dev3.setStyleSheet("font-size: 12pt;") 
        layout.addWidget(dev3)

        # Contato
        contact_title = QLabel(f"{self.util.dict_language[self.lang]['lbl_contact']}:")
        contact_title.setStyleSheet("font-size: 20pt; font-weight: bold; margin-top: 20px;")
        layout.addWidget(contact_title)

        email_label = QLabel("Email:")
        email_label.setStyleSheet("font-size: 15pt; font-weight: bold; margin-top: 5px;")
        layout.addWidget(email_label)

        email1 = QLabel("leonardo.rsfaria91@gmail.com")
        email1.setStyleSheet("font-size: 12pt;")
        layout.addWidget(email1)

        email2 = QLabel("thiago.mancilla@hotmail.com")
        email2.setStyleSheet("font-size: 12pt;")
        
        layout.addWidget(email2)

        email3 = QLabel("valdirgp@univap.br")
        email3.setStyleSheet("font-size: 12pt;")
        layout.addWidget(email3)

        self.root.setCentralWidget(about_widget)
