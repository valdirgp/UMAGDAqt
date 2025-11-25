from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QIcon
import sys
from Controller.MainControl import MainControl
from General.util import Util as util

class UmagdaApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("UMAGDA Application")
        self.setGeometry(100, 100, 1920, 1080)

        self.main_control = MainControl(self)
        self.teste = self.main_control.initialize_app()
    
    def test(self):
        return self.teste

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(util.resource_pathGeneral('images/univap.ico')))
    window = UmagdaApp()
    teste = window.test()
    if teste:
        window.setWindowIcon(QIcon(util.resource_pathGeneral('images/univap.ico')))
        window.showMaximized()
        sys.exit(app.exec_())