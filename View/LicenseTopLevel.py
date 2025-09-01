from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt5.QtCore import Qt
from General.util import Util


class LicenseTopLevel():
    def __init__(self, root, language):
        self.root = root
        self.lang = language
        self.util = Util()

        # elementos que serão criados em load_page()
        self.license_window = None
        self.name_entry = None
        self.inst_entry = None
        self.confirm_button = None

    # cria a janela/toplevel (sem bloquear)
    def load_page(self):
        self.license_window = QDialog(self.root)
        self.license_window.setWindowTitle(self.util.dict_language[self.lang]["lbl_lcr"])
        self.license_window.setFixedSize(220, 150)
        self.license_window.setWindowModality(Qt.ApplicationModal)
        self.license_window.setWindowFlag(Qt.WindowStaysOnTopHint, True)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)

        name_label = QLabel(self.util.dict_language[self.lang]["lbl_name"])
        name_label.setStyleSheet("font-size: 15px;")
        layout.addWidget(name_label)

        self.name_entry = QLineEdit()
        layout.addWidget(self.name_entry)

        inst_label = QLabel(self.util.dict_language[self.lang]["lbl_inst"])
        inst_label.setStyleSheet("font-size: 15px;")
        layout.addWidget(inst_label)

        self.inst_entry = QLineEdit()
        layout.addWidget(self.inst_entry)

        self.confirm_button = QPushButton(self.util.dict_language[self.lang]["btn_confirm"])
        layout.addWidget(self.confirm_button)

        self.license_window.setLayout(layout)

        # exibe a janela (não bloqueante aqui; o bloqueio será feito em bind_get_new_user_info)
        self.license_window.show()

    # vincula o botão confirmar ao callback e espera pela janela (comportamento equivalente ao wait_window)
    def bind_get_new_user_info(self, callback):
        if self.license_window is None:
            raise RuntimeError("Chame load_page() antes de bind_get_new_user_info()")

        # o callback recebe (nome, instituicao, janela) — mesmas coisas que no Tkinter
        self.confirm_button.clicked.connect(
            lambda: callback(self.name_entry.text(), self.inst_entry.text(), self.license_window)
        )

        # bloqueia até o diálogo ser fechado (equivalente ao wait_window)
        self.license_window.exec_()
