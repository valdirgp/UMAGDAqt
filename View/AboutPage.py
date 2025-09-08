'''from General.util import Util
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtGui import QFont

class AboutPage(QWidget):
    def __init__(self, root, language):
        super().__init__(root)
        self.root = root
        self.lang = language
        self.util = Util()

    def load_page(self):
        #self.util.destroy_existent_frames(self.root)

        about_frame = QWidget(self)
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
        about_frame.show()'''

from General.util import Util
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class AboutPage(QWidget):
    def __init__(self, root, language):
        super().__init__(root)
        self.root = root
        self.lang = language
        self.util = Util()

    def load_page(self):
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        # Create frame
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #f5f5f5;
                border-radius: 12px;
                padding: 20px;
            }
            QLabel {
                color: #333;
            }
        """)
        frame_layout = QVBoxLayout(frame)
        frame_layout.setSpacing(20)

        # Title
        title_label = QLabel(self.util.dict_language[self.lang]['menu_about'])
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        frame_layout.addWidget(title_label)

        # Content layout (two columns)
        content_layout = QHBoxLayout()
        content_layout.setSpacing(60)  # distância entre colunas

        # Left column: Names
        left_layout = QVBoxLayout()
        left_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)  # Alinha ao topo e centraliza horizontalmente
        left_label = QLabel(self.util.dict_language[self.lang]['lbl_dev'] + ":")
        left_label.setFont(QFont("Arial", 16, QFont.Bold))
        left_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(left_label)

        names = [
            'Leonardo Rafael dos Santos Faria',
            'Thiago Alexander Moreira Mancilla',
            'Valdir Gill Pillat'
        ]
        for name in names:
            lbl = QLabel(name)
            lbl.setFont(QFont("Arial", 13))
            lbl.setAlignment(Qt.AlignCenter)
            left_layout.addWidget(lbl)

        # Right column: Contacts
        right_layout = QVBoxLayout()
        right_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        right_label = QLabel(self.util.dict_language[self.lang]['lbl_contact'] + ":")
        right_label.setFont(QFont("Arial", 16, QFont.Bold))
        right_label.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(right_label)

        contacts = [
            'leonardo.rsfaria91@gmail.com',
            'thiago.mancilla@hotmail.com',
            'valdirgp@univap.br'
        ]
        for contact in contacts:
            lbl = QLabel(contact)
            lbl.setFont(QFont("Arial", 13))
            lbl.setAlignment(Qt.AlignCenter)
            right_layout.addWidget(lbl)

        # Add columns to content layout
        content_layout.addLayout(left_layout)
        content_layout.addLayout(right_layout)

        # Add content to frame
        frame_layout.addLayout(content_layout)

        # Add frame to main layout
        main_layout.addWidget(frame)
        main_layout.addStretch()
        self.setLayout(main_layout)
        self.setMinimumWidth(500)
        self.setMinimumHeight(350)
