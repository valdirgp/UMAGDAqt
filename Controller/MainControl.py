from Model.License import License
from View.InitialPage import InitialPage
from View.LicenseTopLevel import LicenseTopLevel
from View.AboutPage import AboutPage
from Controller.DownloadsControl import DownloadsControl
from Controller.GraphPageControl import GraphControl
from Controller.CalmDisturbPageControl import CalmDisturbControl
from Controller.CalmPageControl import CalmControl
from General.util import Util
from PyQt5.QtWidgets import QMainWindow, QMenuBar, QMenu, QAction, QApplication
from PyQt5.QtCore import Qt
import sys

class MainControl:
    def __init__(self, root: QMainWindow):
        self.root = root
        self.util = Util()

    def initialize_app(self):
        lang = self.util.get_language_config()
        self.root.setWindowTitle(self.util.dict_language[lang]["title"])
        self.License = License(lang)
        access_allow = self.License.verify_fisical_adress()

        menubar = QMenuBar()
        self.root.setMenuBar(menubar)

        if access_allow:
            magnetic_eq_coords = self.util.calculate_inclination()

            self.DownloadPage = DownloadsControl(self.root, lang, magnetic_eq_coords)
            self.GraphPage = GraphControl(self.root, lang, magnetic_eq_coords)
            self.CalmDisturbPage = CalmDisturbControl(self.root, lang)
            self.CalmPage = CalmControl(self.root, lang)
            self.AboutPage = AboutPage(self.root, lang)

            # Menu principal
            func_menu = QMenu(self.util.dict_language[lang]["menu_main"], self.root)
            func_menu.addAction(QAction(self.util.dict_language[lang]["menu_dwd"], self.root, triggered=self.DownloadPage.load_widgets))
            func_menu.addAction(QAction(self.util.dict_language[lang]["menu_graph"], self.root, triggered=self.GraphPage.load_widgets))
            func_menu.addAction(QAction(self.util.dict_language[lang]["menu_cd"], self.root, triggered=self.CalmDisturbPage.load_widgets))
            func_menu.addAction(QAction(self.util.dict_language[lang]["menu_c"], self.root, triggered=self.CalmPage.load_widgets))

            # Menu de configuração
            config_menu = QMenu(self.util.dict_language[lang]["menu_config"], self.root)
            lang_menu = QMenu(self.util.dict_language[lang]["menu_lang"], self.root)
            lang_menu.addAction(QAction(self.util.dict_language[lang]["menu_en"], self.root, triggered=lambda: self.reset("en")))
            lang_menu.addAction(QAction(self.util.dict_language[lang]["menu_port"], self.root, triggered=lambda: self.reset("br")))
            config_menu.addMenu(lang_menu)

            menubar.addMenu(func_menu)
            menubar.addMenu(config_menu)

            menubar.addAction(QAction(self.util.dict_language[lang]["menu_about"], self.root, triggered=self.AboutPage.load_page))

            self.GraphPage.load_widgets()

        else:
            self.InitialPage = InitialPage(self.root, lang)
            self.LicenseTopLevel = LicenseTopLevel(self.root, lang)
            self.AboutPage = AboutPage(self.root, lang)

            initial_action = QAction(self.util.dict_language[lang]["menu_initial"], self.root, triggered=self.InitialPage.load_page)

            config_menu = QMenu(self.util.dict_language[lang]["menu_config"], self.root)
            lang_menu = QMenu(self.util.dict_language[lang]["menu_lang"], self.root)
            lang_menu.addAction(QAction(self.util.dict_language[lang]["menu_en"], self.root, triggered=lambda: self.reset("en")))
            lang_menu.addAction(QAction(self.util.dict_language[lang]["menu_port"], self.root, triggered=lambda: self.reset("br")))
            config_menu.addMenu(lang_menu)

            menubar.addAction(initial_action)
            menubar.addMenu(config_menu)
            menubar.addAction(QAction(self.util.dict_language[lang]["menu_about"], self.root, triggered=self.AboutPage.load_page))
            menubar.addAction(QAction(self.util.dict_language[lang]["menu_lc"], self.root, triggered=self.create_license_TopLevel))

            self.InitialPage.load_page()

    def create_license_TopLevel(self):
        self.LicenseTopLevel.load_page()
        self.LicenseTopLevel.bind_get_new_user_info(self.License.create_lincense_request)

    def reset(self, lang):
        self.util.change_lang(lang)

        # Fecha a janela atual e recria a aplicação
        self.root.close()

        app = QApplication.instance() or QApplication(sys.argv)
        new_main_window = QMainWindow()
        new_main_window.resize(800, 800)
        new_main_window.showMaximized()

        controller = MainControl(new_main_window)
        controller.initialize_app()

        new_main_window.show()
