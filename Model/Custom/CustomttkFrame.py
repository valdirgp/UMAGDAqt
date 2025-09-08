from PyQt5.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QSizePolicy

class ScrollableFrame(QWidget):
    def __init__(self, parent, width):
        super().__init__(parent)

         # Criação da área de scroll
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        # Frame interno que conterá os widgets
        self.inner_frame = QWidget()
        self.inner_layout = QVBoxLayout()  # <-- aqui definimos o layout interno
        self.inner_frame.setLayout(self.inner_layout)

        # Adiciona o inner_frame ao scroll
        self.scroll_area.setWidget(self.inner_frame)

        # Layout principal do ScrollableFrame
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.addWidget(self.scroll_area)
        self.setLayout(main_layout)

        # Definições de tamanho
        self.setMinimumWidth(width)
        self.setMaximumWidth(width)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)