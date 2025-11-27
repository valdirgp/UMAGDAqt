from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTimer
import sys
from Controller.MainControl import MainControl
from General.util import Util as util

from Model.TelaCarregamento.loading_screen import LoadingScreen
from Model.TelaCarregamento.init_thread import InitThread

class UmagdaApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("UMAGDA Application")
        self.setGeometry(100, 100, 1920, 1080)

        self.main_control = MainControl(self)
        self.teste = self.main_control.initialize_app() # This is now called in InitThread
    
    def test(self):
        return self.teste

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(util.resource_pathGeneral('images/univap.ico')))

    #loading = LoadingScreen()
    #loading.show()
    #app.processEvents()  # Force event processing to show GIF animation
    window = UmagdaApp()
    teste = window.test()
    if teste:
        window.setWindowIcon(QIcon(util.resource_pathGeneral('images/univap.ico')))
        window.showMaximized()
        sys.exit(app.exec_())
    #loading.close()


    '''window = UmagdaApp() # Now non-blocking

    def start_thread():
        # The thread will perform the initialization
        window.thread = InitThread(window.main_control)
        window.thread.finished.connect(lambda ok: finish_loading(ok))
        window.thread.start()

    def finish_loading(success):
        loading.close()
        if success:
            window.showMaximized()
        else:
            print("Falha ao inicializar")
            app.quit()  # Exit the application on initialization failure

    # Start the initialization thread shortly after the event loop starts
    QTimer.singleShot(10, start_thread)

    sys.exit(app.exec_())'''