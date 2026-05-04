from PyQt5.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QSizePolicy
from PyQt5.QtCore import Qt

class ScrollableFrame(QWidget):
    def __init__(self, parent, width, max_width): # 'max' é palavra reservada, mudei para max_width
        super().__init__(parent)

        # Configuração da área de scroll
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        
        # 1. Impede explicitamente o scroll horizontal
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Frame interno
        self.inner_frame = QWidget()
        self.inner_layout = QVBoxLayout(self.inner_frame)
        self.inner_layout.setContentsMargins(5, 5, 25, 5) # Margens evitam que o conteúdo cole na borda
        
        # 2. Garante que o frame interno expanda horizontalmente
        self.inner_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        self.scroll_area.setWidget(self.inner_frame)

        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.scroll_area)

        # Definições de tamanho do widget pai
        self.setMinimumWidth(width)
        self.setMaximumWidth(max_width)
