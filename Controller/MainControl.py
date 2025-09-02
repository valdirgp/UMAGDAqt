'''from Model.License import License
from View.InitialPage import InitialPage
from View.LicenseTopLevel import LicenseTopLevel
from View.AboutPage import AboutPage
from Controller.DownloadsControl import DownloadsControl
from Controller.GraphPageControl import GraphControl
from Controller.CalmDisturbPageControl import CalmDisturbControl
from Controller.CalmPageControl import CalmControl
from General.util import Util
from PyQt5.QtWidgets import QMainWindow, QMenuBar, QMenu, QAction, QApplication

class MainControl():
    def __init__(self, root):
        self.root = root
        self.util = Util()
    
    def initialize_app(self):
        lang = self.util.get_language_config()
        self.root.setWindowTitle(self.util.dict_language[lang]["title"])
        self.License = License(lang)
        acces_allow = self.License.verify_fisical_adress()

        menubar = QMenuBar(self.root)
        self.root.setMenuBar(menubar)

        if acces_allow:
            magnetic_eq_coords = self.util.calculate_inclination()
            self.DownloadPage = DownloadsControl(self.root, lang, magnetic_eq_coords)
            self.GraphPage = GraphControl(self.root, lang, magnetic_eq_coords)
            self.CalmDisturbPage = CalmDisturbControl(self.root, lang)
            self.CalmPage = CalmControl(self.root, lang)

            self.AboutPage = AboutPage(self.root, lang)

            # menu principal
            func_menu = QMenu(self.util.dict_language[lang]["menu_main"], self.root)
            func_menu.addAction(self.util.dict_language[lang]["menu_dwd"], self.DownloadPage.load_widgets)
            func_menu.addAction(self.util.dict_language[lang]["menu_graph"], self.GraphPage.load_widgets)
            func_menu.addAction(self.util.dict_language[lang]['menu_cd'], self.CalmDisturbPage.load_widgets)
            func_menu.addAction(self.util.dict_language[lang]['menu_c'], self.CalmPage.load_widgets)

            # menu de configurações
            config_menu = QMenu(self.util.dict_language[lang]["menu_config"], self.root)
            lang_menu = QMenu(self.util.dict_language[lang]["menu_lang"], self.root)
            lang_menu.addAction(self.util.dict_language[lang]["menu_en"], lambda: self.reset("en"))
            lang_menu.addAction(self.util.dict_language[lang]["menu_port"], lambda: self.reset("br"))
            config_menu.addMenu(lang_menu)

            menubar.addMenu(func_menu)
            menubar.addMenu(config_menu)
            menubar.addAction(self.util.dict_language[lang]["menu_about"], self.AboutPage.load_page)

            self.GraphPage.load_widgets()

        else:

            self.InitialPage = InitialPage(self.root, lang)
            self.LicenseTopLevel = LicenseTopLevel(self.root, lang)
            self.AboutPage = AboutPage(self.root, lang)

            menubar.addAction(self.util.dict_language[lang]["menu_initial"], self.InitialPage.load_page)

            config_menu = QMenu(self.util.dict_language[lang]["menu_config"], self.root)
            lang_menu = QMenu(self.util.dict_language[lang]["menu_lang"], self.root)
            lang_menu.addAction(self.util.dict_language[lang]["menu_en"], lambda: self.reset("en"))
            lang_menu.addAction(self.util.dict_language[lang]["menu_port"], lambda: self.reset("br"))
            config_menu.addMenu(lang_menu)

            menubar.addMenu(config_menu)
            menubar.addAction(self.util.dict_language[lang]["menu_about"], self.AboutPage.load_page)
            menubar.addAction(self.util.dict_language[lang]["menu_lc"], self.create_license_TopLevel)

            self.InitialPage.load_page()
    
    def create_license_TopLevel(self):
        self.LicenseTopLevel.load_page()
        self.LicenseTopLevel.bind_get_new_user_info(self.License.create_lincense_request)

    def reset(self, lang):
        self.util.change_lang(lang)
        self.root.close()

        new_root = QMainWindow()
        new_root.resize(800, 800)
        new_root.showMaximized()
        app = MainControl(new_root)
        app.initialize_app()
        new_root.show()

'''

from Model.License import License
from View.InitialPage import InitialPage
from View.LicenseTopLevel import LicenseTopLevel
from View.AboutPage import AboutPage
from Controller.DownloadsControl import DownloadsControl
from Controller.GraphPageControl import GraphControl
from Controller.CalmDisturbPageControl import CalmDisturbControl
from Controller.CalmPageControl import CalmControl
from General.util import Util

from PyQt5.QtWidgets import (
    QMainWindow, QMenuBar, QMenu, QStackedWidget
)


class MainControl:
    def __init__(self, root: QMainWindow):
        self.root = root
        self.util = Util()
        self.stack = QStackedWidget()
        self.root.setCentralWidget(self.stack)


    def initialize_app(self):
        lang = self.util.get_language_config()
        self.root.setWindowTitle(self.util.dict_language[lang]["title"])
        self.License = License(lang)
        access_allow = self.License.verify_fisical_adress()

        menubar = QMenuBar(self.root)
        self.root.setMenuBar(menubar)

        if access_allow:
            magnetic_eq_coords = self.util.calculate_inclination()
            self.DownloadPage = DownloadsControl(self.root, lang, magnetic_eq_coords)
            self.DownloadPage.load_widgets()
        
            #self.GraphPage = GraphControl(self.root, lang, magnetic_eq_coords)
            #self.GraphPage.load_widgets()
            #self.CalmDisturbPage = CalmDisturbControl(self.root, lang)
            #self.CalmPage = CalmControl(self.root, lang)

            #self.AboutPage = AboutPage(self.root, lang)

            # adiciona páginas ao stack
            self.stack.addWidget(self.DownloadPage.get_widget())
            #self.stack.addWidget(self.GraphPage.get_widget())
            #self.stack.addWidget(self.CalmDisturbPage)
            #self.stack.addWidget(self.CalmPage)

            # menu principal
            func_menu = QMenu(self.util.dict_language[lang]["menu_main"], self.root)
            func_menu.addAction(self.util.dict_language[lang]["menu_dwd"], lambda: self.stack.setCurrentWidget(self.DownloadPage.get_widget()))
            #func_menu.addAction(self.util.dict_language[lang]["menu_graph"], lambda: self.stack.setCurrentWidget(self.GraphPage.get_widget()))
            
            #func_menu.addAction(self.util.dict_language[lang]['menu_cd'], lambda: self.stack.setCurrentWidget(self.CalmDisturbPage))
            #func_menu.addAction(self.util.dict_language[lang]['menu_c'], lambda: self.stack.setCurrentWidget(self.CalmPage))

            # menu de configurações
            config_menu = QMenu(self.util.dict_language[lang]["menu_config"], self.root)
            lang_menu = QMenu(self.util.dict_language[lang]["menu_lang"], self.root)
            lang_menu.addAction(self.util.dict_language[lang]["menu_en"], lambda: self.reset("en"))
            lang_menu.addAction(self.util.dict_language[lang]["menu_port"], lambda: self.reset("br"))
            config_menu.addMenu(lang_menu)

            menubar.addMenu(func_menu)
            menubar.addMenu(config_menu)
            #menubar.addAction(self.util.dict_language[lang]["menu_about"], self.AboutPage.load_page)

            # abre página inicial
            #self.stack.setCurrentWidget(self.GraphPage)
            self.stack.setCurrentWidget(self.DownloadPage.get_widget())

        else:
            self.InitialPage = InitialPage(self.root, lang)
            self.LicenseTopLevel = LicenseTopLevel(self.root, lang)
            self.AboutPage = AboutPage(self.root, lang)

            self.stack.addWidget(self.InitialPage)

            menubar.addAction(self.util.dict_language[lang]["menu_initial"], lambda: self.stack.setCurrentWidget(self.InitialPage))

            config_menu = QMenu(self.util.dict_language[lang]["menu_config"], self.root)
            lang_menu = QMenu(self.util.dict_language[lang]["menu_lang"], self.root)
            lang_menu.addAction(self.util.dict_language[lang]["menu_en"], lambda: self.reset("en"))
            lang_menu.addAction(self.util.dict_language[lang]["menu_port"], lambda: self.reset("br"))
            config_menu.addMenu(lang_menu)

            menubar.addMenu(config_menu)
            menubar.addAction(self.util.dict_language[lang]["menu_about"], self.AboutPage.load_page)
            menubar.addAction(self.util.dict_language[lang]["menu_lc"], self.create_license_TopLevel)

            self.stack.setCurrentWidget(self.InitialPage)

    def create_license_TopLevel(self):
        self.LicenseTopLevel.load_page()
        self.LicenseTopLevel.bind_get_new_user_info(self.License.create_lincense_request)

    def reset(self, lang):
        self.util.change_lang(lang)
        self.root.close()

        new_root = QMainWindow()
        new_root.resize(800, 800)
        new_root.showMaximized()
        app = MainControl(new_root)
        app.initialize_app()
        new_root.show()
