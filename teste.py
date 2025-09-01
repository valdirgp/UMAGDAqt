# teste.py

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget

class TestApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("UMAGDA Test Application")
        self.setGeometry(100, 100, 600, 400)

        layout = QVBoxLayout()
        label = QLabel("This is a test application for UMAGDA using PyQt.")
        layout.addWidget(label)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestApp()
    window.show()
    sys.exit(app.exec_())