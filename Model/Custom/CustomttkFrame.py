from PyQt5.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QSizePolicy

class ScrollableFrame(QWidget):
    def __init__(self, parent, width):
        super().__init__(parent)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.inner_frame = QWidget()
        self.inner_layout = QVBoxLayout()  # não passar parent aqui!
        self.inner_frame.setLayout(self.inner_layout)

        self.scroll_area.setWidget(self.inner_frame)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget(self.scroll_area)
        self.setLayout(layout)

        self.setMinimumWidth(width)
        self.setMaximumWidth(width)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)