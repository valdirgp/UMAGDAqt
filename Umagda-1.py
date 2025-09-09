from PyQt5.QtWidgets import QApplication, QMainWindow
import sys
from Controller.MainControl import MainControl

class UmagdaApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("UMAGDA Application")
        self.setGeometry(100, 100, 1920, 1080)

        self.main_control = MainControl(self)
        self.main_control.initialize_app()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = UmagdaApp()
    window.showMaximized()
    sys.exit(app.exec_())