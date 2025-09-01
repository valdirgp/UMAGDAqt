from PyQt5.QtWidgets import QWidget, QVBoxLayout, QScrollArea

class ScrollableFrame(QWidget):
    def __init__(self, parent, width):
        super().__init__(parent)

        # Criando o QScrollArea
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFixedWidth(width)

        # Criando o widget interno
        self.inner_frame = QWidget()
        self.inner_frame.setFixedWidth(width)
        self.inner_layout = QVBoxLayout(self.inner_frame)
        self.inner_frame.setLayout(self.inner_layout)

        # Adicionando o widget interno ao QScrollArea
        self.scroll_area.setWidget(self.inner_frame)

        # Layout principal do ScrollableFrame
        layout = QVBoxLayout()
        layout.addWidget(self.scroll_area)
        self.setLayout(layout)