from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout, QFormLayout
from PyQt5.QtCore import Qt
from General.util import Util

class LicenseTopLevel:
    def __init__(self, root, language):
        self.root = root  # Espera-se que seja QMainWindow ou QWidget
        self.lang = language
        self.util = Util()
        self.license_window = None  # QDialog será criado em `load_page`

    def load_page(self):
        self.license_window = QDialog(self.root)
        self.license_window.setWindowTitle(self.util.dict_language[self.lang]["lbl_lcr"])
        self.license_window.setFixedSize(300, 180)
        self.license_window.setWindowModality(Qt.ApplicationModal)  # Bloqueia interação com janela principal
        self.license_window.setAttribute(Qt.WA_DeleteOnClose)

        form_layout = QFormLayout()

        # Campo nome
        self.name_entry = QLineEdit()
        form_layout.addRow(QLabel(self.util.dict_language[self.lang]["lbl_name"]), self.name_entry)

        # Campo instituição
        self.inst_entry = QLineEdit()
        form_layout.addRow(QLabel(self.util.dict_language[self.lang]["lbl_inst"]), self.inst_entry)

        # Botão de confirmar
        self.confirm_button = QPushButton(self.util.dict_language[self.lang]["btn_confirm"])
        layout = QVBoxLayout()
        layout.addLayout(form_layout)
        layout.addWidget(self.confirm_button, alignment=Qt.AlignCenter)

        self.license_window.setLayout(layout)

        # Exibe a janela de forma modal
        self.license_window.exec_()

    def bind_get_new_user_info(self, callback):
        self.confirm_button.clicked.connect(lambda: callback(
            self.name_entry.text(),
            self.inst_entry.text(),
            self.license_window
        ))
