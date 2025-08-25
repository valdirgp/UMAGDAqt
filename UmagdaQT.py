from Controller.MainControl import MainControl
from PyQt5.QtWidgets import QMainWindow, QApplication
import sys

class UmagdaQT(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("UmagdaQT")
        self.resize(900, 700)
        self.showMaximized()
        
        self.app_controller = MainControl(self)
        self.app_controller.initialize_app()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = UmagdaQT()
    main_window.show()
    sys.exit(app.exec_())
