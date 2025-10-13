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
    QMainWindow, QMenuBar, QMenu, QStackedWidget, QWidgetAction, QComboBox, QDateEdit
)
from PyQt5.QtCore import QDate
from PyQt5.QtGui import QIcon
from datetime import datetime
import psutil

#from PyQt5.QtCore import QFileSystemWatcher

class MainControl:
    def __init__(self, root: QMainWindow):
        self.root = root
        self.util = Util()
        self.stack = QStackedWidget()
        self.root.setCentralWidget(self.stack)
        #self.watcher = QFileSystemWatcher()


    def initialize_app(self):
        self.lang = self.util.get_language_config()
        self.year = self.util.get_year_config()
        self.final = self.util.get_final_config()
        self.drive = self.util.get_drive_config()
        self.root.setWindowTitle(self.util.dict_language[self.lang]["title"])
        self.License = License(self.lang)
        access_allow = self.License.verify_fisical_adress()

        menubar = QMenuBar(self.root)
        self.root.setMenuBar(menubar)

        if access_allow:
            magnetic_eq_coords = self.util.calculate_inclination(self.year)

            self.DownloadPage = DownloadsControl(self.root, self.lang, self.year, self.drive, magnetic_eq_coords)
            self.DownloadPage.load_widgets()
        
            self.GraphPage = GraphControl(self.root, self.lang, self.year, self.final, self.drive, magnetic_eq_coords)
            self.GraphPage.load_widgets()

            self.CalmDisturbPage = CalmDisturbControl(self.root, self.lang, self.year, self.final, self.drive, magnetic_eq_coords)
            self.CalmDisturbPage.load_widgets()

            self.CalmPage = CalmControl(self.root, self.lang, self.year, self.final, self.drive, magnetic_eq_coords)
            self.CalmPage.load_widgets()

            self.UniversalCDPage = UniversalCDPageControl(self.root, self.lang, self.year, self.final, self.drive, magnetic_eq_coords)
            self.UniversalCDPage.load_widgets()

            self.AboutPage = AboutPage(self.root, self.lang)
            self.AboutPage.load_page()

            # adiciona páginas ao stack
            self.stack.addWidget(self.DownloadPage.get_widget())
            self.stack.addWidget(self.GraphPage.get_widget())
            self.stack.addWidget(self.CalmDisturbPage.get_widget())
            self.stack.addWidget(self.CalmPage.get_widget())
            self.stack.addWidget(self.UniversalCDPage.get_widget())

            self.stack.addWidget(self.AboutPage)

            # menu principal
            func_menu = QMenu(self.util.dict_language[self.lang]["menu_main"], self.root)

            func_menu.addAction(self.util.dict_language[self.lang]["menu_dwd"], lambda: self.stack.setCurrentWidget(self.DownloadPage.get_widget()))
            func_menu.addAction(self.util.dict_language[self.lang]["menu_graph"], lambda: self.stack.setCurrentWidget(self.GraphPage.get_widget()))
            func_menu.addAction(self.util.dict_language[self.lang]['menu_cd'], lambda: self.stack.setCurrentWidget(self.CalmDisturbPage.get_widget()))
            func_menu.addAction(self.util.dict_language[self.lang]['menu_c'], lambda: self.stack.setCurrentWidget(self.CalmPage.get_widget()))
            func_menu.addAction(self.util.dict_language[self.lang]['menu_ucd'], lambda: self.stack.setCurrentWidget(self.UniversalCDPage.get_widget()))

            # menu de configurações
            config_menu = QMenu(self.util.dict_language[self.lang]["menu_config"], self.root)
            lang_menu = QMenu(self.util.dict_language[self.lang]["menu_lang"], self.root)
            lang_menu.addAction(self.util.dict_language[self.lang]["menu_en"], lambda: self.reset("en"))
            lang_menu.addAction(self.util.dict_language[self.lang]["menu_port"], lambda: self.reset("br"))
            config_menu.addMenu(lang_menu)

            # Criar submenu de data
            date_menu = QMenu(self.util.dict_language[self.lang]["menu_date"], self.root)

            # Criar o QDateEdit (input de data)
            date_edit = QDateEdit()
            date_edit.setCalendarPopup(True)  # Habilita o calendário ao clicar
            date_edit.setDisplayFormat("dd/MM/yyyy")  # Formato brasileiro
            date_edit.setMinimumSize(85, 25)
            # Definir data inicial
            initial_date = QDate(self.year[2], self.year[1], self.year[0])
            date_edit.setDate(initial_date)
            date_edit.setMinimumDate(QDate(1900, 1, 1))
            ano_atual = datetime.now().year
            mes_atual = datetime.now().month
            dia_atual = datetime.now().day
            date_edit.setMaximumDate(QDate(ano_atual, mes_atual, dia_atual))

            # Colocar o widget no menu usando QWidgetAction
            date_action = QWidgetAction(self.root)
            date_action.setDefaultWidget(date_edit)

            date_edit_final = QDateEdit()
            date_edit_final.setCalendarPopup(True)  # Habilita o calendário ao clicar
            date_edit_final.setDisplayFormat("dd/MM/yyyy")  # Formato brasileiro
            date_edit_final.setMinimumSize(85, 25)
            # Definir data inicial
            initial_date_final = QDate(self.final[2], self.final[1], self.final[0])
            date_edit_final.setDate(initial_date_final)
            date_edit_final.setMinimumDate(QDate(1900, 1, 1))
            date_edit_final.setMaximumDate(QDate(ano_atual, mes_atual, dia_atual))

            # Colocar o widget no menu usando QWidgetAction
            date_action_final = QWidgetAction(self.root)
            date_action_final.setDefaultWidget(date_edit_final)
            
            # Adicionar ao menu e depois ao menu principal
            date_menu.addAction(date_action)
            date_menu.addAction(date_action_final)
            date_menu.addAction(self.util.dict_language[self.lang]["btn_confirm"], lambda: confirm_date())
            config_menu.addMenu(date_menu)

            def confirm_date():
                selected_date = date_edit.date()
                selected_date_final = date_edit_final.date()
                
                if selected_date.day() != self.year[0] or selected_date.month() != self.year[1] or selected_date.year() != self.year[2]:
                    self.util.change_year(
                        year=[selected_date.day(), selected_date.month(), selected_date.year()]                  
                    )
                if selected_date_final.day() != self.final[0] or selected_date_final.month() != self.final[1] or selected_date_final.year() != self.final[2]:
                    self.util.change_final(
                        final=[selected_date_final.day(), selected_date_final.month(), selected_date_final.year()]                  
                    )
                self.reset(self.lang)

            drive_menu = QMenu(self.util.dict_language[self.lang]["menu_drive"], self.root)

            drive_combo = QComboBox()

            # Listar drives disponíveis
            for part in psutil.disk_partitions(all=False):
                drive_combo.addItem(part.device)  # exemplo: "C:\", "D:\"

            index = drive_combo.findText(self.drive)
            if index != -1:  # se encontrou
                drive_combo.setCurrentIndex(index)

            # Criar widgetAction para colocar dentro do menu
            drive_action = QWidgetAction(self.root)
            drive_action.setDefaultWidget(drive_combo)

            drive_menu.addAction(drive_action)
            config_menu.addMenu(drive_menu)

            # Exemplo: ação ao trocar drive
            drive_combo.currentTextChanged.connect(lambda: self.util.change_drive(drive_combo.currentText()))

            config_menu.addAction(self.util.dict_language[self.lang]["menu_reset"], lambda: self.reset())

            menubar.addMenu(func_menu)
            menubar.addMenu(config_menu)
            menubar.addAction(self.util.dict_language[self.lang]["menu_about"], lambda: self.stack.setCurrentWidget(self.AboutPage))

            # abre página inicial
            self.stack.setCurrentWidget(self.GraphPage.get_widget())

            #path = "General/config.txt"
            #self.watcher.addPath(path)
            #self.watcher.fileChanged.connect(self.update_listbox_on_change)
            #self.watcher.fileChanged.connect(self.reset)

        else:
            self.InitialPage = InitialPage(self.root, self.lang)
            self.InitialPage.load_page()

            self.LicenseTopLevel = LicenseTopLevel(self.root, self.lang)
            #self.LicenseTopLevel.load_page()

            self.AboutPage = AboutPage(self.root, self.lang)
            self.AboutPage.load_page()

            self.stack.addWidget(self.InitialPage)
            self.stack.addWidget(self.AboutPage)

            menubar.addAction(self.util.dict_language[self.lang]["menu_initial"], lambda: self.stack.setCurrentWidget(self.InitialPage))

            config_menu = QMenu(self.util.dict_language[self.lang]["menu_config"], self.root)
            lang_menu = QMenu(self.util.dict_language[self.lang]["menu_lang"], self.root)
            lang_menu.addAction(self.util.dict_language[self.lang]["menu_en"], lambda: self.reset("en"))
            lang_menu.addAction(self.util.dict_language[self.lang]["menu_port"], lambda: self.reset("br"))
            config_menu.addMenu(lang_menu)

            menubar.addMenu(config_menu)
            menubar.addAction(self.util.dict_language[self.lang]["menu_about"], lambda: self.stack.setCurrentWidget(self.AboutPage))
            menubar.addAction(self.util.dict_language[self.lang]["menu_lc"], self.create_license_TopLevel)

            self.stack.setCurrentWidget(self.InitialPage)

    def update_listbox_on_change(self):
        if self.year != self.util.get_year_config() or self.final != self.util.get_final_config():
            self.initialize_app()
        
    def restart_pages(self):
        pass

    def create_license_TopLevel(self):
        self.LicenseTopLevel.load_page()
        self.LicenseTopLevel.bind_get_new_user_info(self.License.create_lincense_request)

    def reset(self, lang="", *args, **kwargs):
        if lang not in ("", "en", "br"):
            lang = ""

        if lang != "":
            self.util.change_lang(lang)

        self.root.close()

        new_root = QMainWindow()
        new_root.resize(1920, 1080)
        new_root.showMaximized()
        new_root.setWindowIcon(QIcon(self.util.resource_path('images/univap.ico')))
        app = MainControl(new_root)
        app.initialize_app()
        new_root.show()
