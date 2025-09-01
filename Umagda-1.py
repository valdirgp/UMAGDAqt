from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget
import sys
from Controller.MainControl import MainControl

class UmagdaApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("UMAGDA Application")
        self.setGeometry(100, 100, 800, 600)

        # QStackedWidget como central
        self.stacked_widget = QStackedWidget(self)
        self.setCentralWidget(self.stacked_widget)

        # Agora passamos o QMainWindow para MainControl, não o stacked
        self.main_control = MainControl(self)
        self.main_control.initialize_app()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = UmagdaApp()
    window.showMaximized()
    sys.exit(app.exec_())


'''from PyQt5.QtWidgets import QApplication, QMainWindow
import sys
from Controller.MainControl import MainControl

class UmagdaApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("UMAGDA Application")
        self.setGeometry(100, 100, 800, 600)

        # Inicializa o controller passando o QMainWindow inteiro
        self.main_control = MainControl(self)
        self.main_control.initialize_app()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = UmagdaApp()
    window.showMaximized()
    sys.exit(app.exec_())'''
