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
from Controller.UniversalCDPageControl import UniversalCDPageControl
from General.util import Util

from PyQt5.QtWidgets import (
    QMainWindow, QMenuBar, QMenu, QStackedWidget, QSpinBox, QWidgetAction, QComboBox, QDateEdit
)
from PyQt5.QtCore import QDate
from PyQt5.QtGui import QIcon
from datetime import datetime
import psutil


class MainControl:
    def __init__(self, root: QMainWindow):
        self.root = root
        self.util = Util()
        self.stack = QStackedWidget()
        self.root.setCentralWidget(self.stack)


    def initialize_app(self):
        lang = self.util.get_language_config()
        year = self.util.get_year_config()
        drive = self.util.get_drive_config()
        self.root.setWindowTitle(self.util.dict_language[lang]["title"])
        self.License = License(lang)
        access_allow = self.License.verify_fisical_adress()

        menubar = QMenuBar(self.root)
        self.root.setMenuBar(menubar)

        if access_allow:
            magnetic_eq_coords = self.util.calculate_inclination(year[2])

            self.DownloadPage = DownloadsControl(self.root, lang, year, drive, magnetic_eq_coords)
            self.DownloadPage.load_widgets()
        
            self.GraphPage = GraphControl(self.root, lang, year, drive, magnetic_eq_coords)
            self.GraphPage.load_widgets()

            self.CalmDisturbPage = CalmDisturbControl(self.root, lang, year, drive, magnetic_eq_coords)
            self.CalmDisturbPage.load_widgets()

            self.CalmPage = CalmControl(self.root, lang, year, drive, magnetic_eq_coords)
            self.CalmPage.load_widgets()

            self.UniversalCDPage = UniversalCDPageControl(self.root, lang, year, drive, magnetic_eq_coords)
            self.UniversalCDPage.load_widgets()

            self.AboutPage = AboutPage(self.root, lang)
            self.AboutPage.load_page()

            # adiciona páginas ao stack
            self.stack.addWidget(self.DownloadPage.get_widget())
            self.stack.addWidget(self.GraphPage.get_widget())
            self.stack.addWidget(self.CalmDisturbPage.get_widget())
            self.stack.addWidget(self.CalmPage.get_widget())
            self.stack.addWidget(self.UniversalCDPage.get_widget())

            self.stack.addWidget(self.AboutPage)

            # menu principal
            func_menu = QMenu(self.util.dict_language[lang]["menu_main"], self.root)

            func_menu.addAction(self.util.dict_language[lang]["menu_dwd"], lambda: self.stack.setCurrentWidget(self.DownloadPage.get_widget()))
            func_menu.addAction(self.util.dict_language[lang]["menu_graph"], lambda: self.stack.setCurrentWidget(self.GraphPage.get_widget()))
            func_menu.addAction(self.util.dict_language[lang]['menu_cd'], lambda: self.stack.setCurrentWidget(self.CalmDisturbPage.get_widget()))
            func_menu.addAction(self.util.dict_language[lang]['menu_c'], lambda: self.stack.setCurrentWidget(self.CalmPage.get_widget()))
            func_menu.addAction(self.util.dict_language[lang]['menu_ucd'], lambda: self.stack.setCurrentWidget(self.UniversalCDPage.get_widget()))

            #func_menu.addAction(self.util.dict_language[lang]["menu_about"], lambda: self.stack.setCurrentWidget(self.AboutPage))

            # menu de configurações
            config_menu = QMenu(self.util.dict_language[lang]["menu_config"], self.root)
            lang_menu = QMenu(self.util.dict_language[lang]["menu_lang"], self.root)
            lang_menu.addAction(self.util.dict_language[lang]["menu_en"], lambda: self.reset("en"))
            lang_menu.addAction(self.util.dict_language[lang]["menu_port"], lambda: self.reset("br"))
            config_menu.addMenu(lang_menu)

            '''
            year_menu = QMenu(self.util.dict_language[lang]["menu_year"], self.root)

            # Campo de ano com setinhas
            year_spin = QSpinBox()
            year_spin.setRange(1900, 2100)   # limite mínimo e máximo
            year_spin.setValue(year)         # valor inicial

            # Criar um widgetAction para colocar o spinbox dentro do menu
            year_action = QWidgetAction(self.root)
            year_action.setDefaultWidget(year_spin)

            year_menu.addAction(year_action)
            config_menu.addMenu(year_menu)

            # Exemplo: conectando a mudança de valor
            # Exemplo: chamar função só quando perder o foco (ou Enter)
            year_spin.editingFinished.connect(lambda: self.util.change_year(year_spin.value()))
            '''

            # Criar submenu de data
            date_menu = QMenu(self.util.dict_language[lang]["menu_date"], self.root)

            # Criar o QDateEdit (input de data)
            date_edit = QDateEdit()
            date_edit.setCalendarPopup(True)  # Habilita o calendário ao clicar
            date_edit.setDisplayFormat("dd/MM/yyyy")  # Formato brasileiro

            # Definir data inicial
            initial_date = QDate(year[2], year[1], year[0])
            date_edit.setDate(initial_date)
            date_edit.setMinimumDate(QDate(1900, 1, 1))
            ano_atual = datetime.now().year
            mes_atual = datetime.now().month
            dia_atual = datetime.now().day
            date_edit.setMaximumDate(QDate(ano_atual, mes_atual, dia_atual))

            # Colocar o widget no menu usando QWidgetAction
            date_action = QWidgetAction(self.root)
            date_action.setDefaultWidget(date_edit)

            # Adicionar ao menu e depois ao menu principal
            date_menu.addAction(date_action)
            config_menu.addMenu(date_menu)

            # Conectar o evento de edição finalizada (quando perde o foco ou aperta Enter)
            def update_date():
                selected_date = date_edit.date()
                self.util.change_year(
                    year=[selected_date.day(), selected_date.month(), selected_date.year()]                  
                )

            date_edit.editingFinished.connect(update_date)

            drive_menu = QMenu(self.util.dict_language[lang]["menu_drive"], self.root)

            # Criar combobox
            drive_combo = QComboBox()

            # Listar drives disponíveis
            for part in psutil.disk_partitions(all=False):
                drive_combo.addItem(part.device)  # exemplo: "C:\", "D:\"

            index = drive_combo.findText(drive)
            if index != -1:  # se encontrou
                drive_combo.setCurrentIndex(index)

            # Criar widgetAction para colocar dentro do menu
            drive_action = QWidgetAction(self.root)
            drive_action.setDefaultWidget(drive_combo)

            drive_menu.addAction(drive_action)
            config_menu.addMenu(drive_menu)

            # Exemplo: ação ao trocar drive
            drive_combo.currentTextChanged.connect(lambda: self.util.change_drive(drive_combo.currentText()))

            config_menu.addAction(self.util.dict_language[lang]["menu_reset"], lambda: self.reset())

            menubar.addMenu(func_menu)
            menubar.addMenu(config_menu)
            menubar.addAction(self.util.dict_language[lang]["menu_about"], lambda: self.stack.setCurrentWidget(self.AboutPage))

            # abre página inicial
            self.stack.setCurrentWidget(self.GraphPage.get_widget())

        else:
            self.InitialPage = InitialPage(self.root, lang)
            self.InitialPage.load_page()

            self.LicenseTopLevel = LicenseTopLevel(self.root, lang)
            #self.LicenseTopLevel.load_page()

            self.AboutPage = AboutPage(self.root, lang)
            self.AboutPage.load_page()

            self.stack.addWidget(self.InitialPage)
            self.stack.addWidget(self.AboutPage)

            menubar.addAction(self.util.dict_language[lang]["menu_initial"], lambda: self.stack.setCurrentWidget(self.InitialPage))

            config_menu = QMenu(self.util.dict_language[lang]["menu_config"], self.root)
            lang_menu = QMenu(self.util.dict_language[lang]["menu_lang"], self.root)
            lang_menu.addAction(self.util.dict_language[lang]["menu_en"], lambda: self.reset("en"))
            lang_menu.addAction(self.util.dict_language[lang]["menu_port"], lambda: self.reset("br"))
            config_menu.addMenu(lang_menu)

            menubar.addMenu(config_menu)
            menubar.addAction(self.util.dict_language[lang]["menu_about"], lambda: self.stack.setCurrentWidget(self.AboutPage))
            menubar.addAction(self.util.dict_language[lang]["menu_lc"], self.create_license_TopLevel)

            self.stack.setCurrentWidget(self.InitialPage)

    def create_license_TopLevel(self):
        self.LicenseTopLevel.load_page()
        self.LicenseTopLevel.bind_get_new_user_info(self.License.create_lincense_request)

    def reset(self, lang=""):
        lang = self.util.get_language_config() if lang == "" else lang
        self.util.change_lang(lang)
        self.root.close()

        new_root = QMainWindow()
        new_root.resize(1920, 1080)
        new_root.showMaximized()
        new_root.setWindowIcon(QIcon('General/images/univap.ico'))
        app = MainControl(new_root)
        app.initialize_app()
        new_root.show()
