from PyQt5.QtWidgets import QWidget, QScrollArea, QVBoxLayout, QSizePolicy
from PyQt5.QtCore import Qt

class ScrollableFrame(QWidget):
    def __init__(self, parent=None, width=400):
        super().__init__(parent)

        self.setMinimumWidth(width)

        # Criar o layout principal do widget
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Criar QScrollArea
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Widget interno que conterá os conteúdos roláveis
        self.inner_widget = QWidget()
        self.inner_widget.setMinimumWidth(width)

        # Layout para o widget interno (onde você vai adicionar seus widgets)
        self.inner_layout = QVBoxLayout(self.inner_widget)
        self.inner_layout.setContentsMargins(0, 0, 0, 0)
        self.inner_layout.setSpacing(0)

        # Configurar scroll area para conter o inner_widget
        self.scroll_area.setWidget(self.inner_widget)

        # Adicionar o scroll area ao layout principal
        layout.addWidget(self.scroll_area)

    def addWidget(self, widget):
        """Método para adicionar widgets ao frame interno."""
        self.inner_layout.addWidget(widget)
