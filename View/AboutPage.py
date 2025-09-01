from General.util import Util
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtGui import QFont

class AboutPage(QWidget):
    def __init__(self, root, language):
        super().__init__(root)
        self.root = root
        self.lang = language
        self.util = Util()

    def load_page(self):
        self.util.destroy_existent_frames(self.root)

        about_frame = QWidget(self.root)
        about_layout = QVBoxLayout(about_frame)
        about_frame.setLayout(about_layout)
        about_frame.show()

        # Developer section
        dev_label = QLabel(f"{self.util.dict_language[self.lang]['lbl_dev']}:")
        dev_label.setFont(QFont("Arial", 20, QFont.Bold))
        about_layout.addWidget(dev_label)
        dev1 = QLabel('Leonardo Rafael dos Santos Faria')
        dev1.setFont(QFont("Arial", 12))
        about_layout.addWidget(dev1)
        dev2 = QLabel('Thiago Alexander Moreira Mancilla')
        dev2.setFont(QFont("Arial", 12))
        about_layout.addWidget(dev2)
        dev3 = QLabel('Valdir Gill Pillat')
        dev3.setFont(QFont("Arial", 12))
        about_layout.addWidget(dev3)

        # Spacer
        about_layout.addSpacing(10)

        # Contact section
        contact_label = QLabel(f"{self.util.dict_language[self.lang]['lbl_contact']}:")
        contact_label.setFont(QFont("Arial", 20, QFont.Bold))
        about_layout.addWidget(contact_label)
        email_label = QLabel('Email:')
        email_label.setFont(QFont("Arial", 15, QFont.Bold))
        about_layout.addWidget(email_label)
        email1 = QLabel('leonardo.rsfaria91@gmail.com')
        email1.setFont(QFont("Arial", 12))
        about_layout.addWidget(email1)
        email2 = QLabel('thiago.mancilla@hotmail.com')
        email2.setFont(QFont("Arial", 12))
        about_layout.addWidget(email2)
        email3 = QLabel('valdirgp@univap.br')
        email3.setFont(QFont("Arial", 12))
        about_layout.addWidget(email3)

        about_frame.setLayout(about_layout)
        about_frame.setMinimumWidth(400)
        about_frame.setMinimumHeight(300)
        about_frame.show()