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
    QMainWindow, QMenuBar, QMenu, QStackedWidget, 
    QWidgetAction, QComboBox, QDateEdit, QMessageBox
)
from PyQt5.QtCore import QDate, QFileSystemWatcher
from PyQt5.QtGui import QIcon
from datetime import datetime
import psutil


class MainControl:
    def __init__(self, root: QMainWindow):
        self.root = root
        self.util = Util()
        self.stack = QStackedWidget()
        self.root.setCentralWidget(self.stack)

        self.watcher = QFileSystemWatcher()
        path = self.util.resource_path("config.txt")
        self.watcher.addPath(path)
        self.watcher.fileChanged.connect(self.insertMap)

    def initialize_app(self):
        self.util.createConfig()
        try:
            self.lang = self.util.get_language_config()
            self.year = self.util.get_year_config()
            self.final = self.util.get_final_config()
            self.drive = self.util.get_drive_config()
            self.root.setWindowTitle(self.util.dict_language[self.lang]["title"])
            self.License = License(self.lang)
            access_allow = self.License.verify_fisical_adress()

            menubar = QMenuBar(self.root)
            self.root.setMenuBar(menubar)
        except:
            QMessageBox.information(
                None,
                "Error",
                "config.txt not found"
            )
            return False

        if access_allow:
            magnetic_eq_coords = self.util.calculate_inclination(self.year)

            self.DownloadControl = DownloadsControl(self.root, self.lang, self.year, self.drive, magnetic_eq_coords)
            self.DownloadControl.load_widgets()
            self.DownloadPage = self.DownloadControl.get_widget()
        
            self.GraphControl = GraphControl(self.root, self.lang, self.year, self.final, self.drive, magnetic_eq_coords)
            self.GraphControl.load_widgets()
            self.GraphPage = self.GraphControl.get_widget()

            self.CalmDisturbControl = CalmDisturbControl(self.root, self.lang, self.year, self.final, self.drive, magnetic_eq_coords)
            self.CalmDisturbControl.load_widgets()
            self.CalmDisturbPage = self.CalmDisturbControl.get_widget()

            self.CalmControl = CalmControl(self.root, self.lang, self.year, self.final, self.drive, magnetic_eq_coords)
            self.CalmControl.load_widgets()
            self.CalmPage = self.CalmControl.get_widget()

            self.UniversalCDControl = UniversalCDPageControl(self.root, self.lang, self.year, self.final, self.drive, magnetic_eq_coords)
            self.UniversalCDControl.load_widgets()
            self.UniversalCDPage = self.UniversalCDControl.get_widget()

            self.AboutPage = AboutPage(self.root, self.lang)
            self.AboutPage.load_page()

            # adiciona páginas ao stack
            self.stack.addWidget(self.DownloadPage)
            self.stack.addWidget(self.GraphPage)
            self.stack.addWidget(self.CalmDisturbPage)
            self.stack.addWidget(self.CalmPage)
            self.stack.addWidget(self.UniversalCDPage)

            self.stack.addWidget(self.AboutPage)

            # menu principal
            func_menu = QMenu(self.util.dict_language[self.lang]["menu_main"], self.root)

            func_menu.addAction(self.util.dict_language[self.lang]["menu_dwd"], lambda: self.stack.setCurrentWidget(self.DownloadPage))
            func_menu.addAction(self.util.dict_language[self.lang]["menu_graph"], lambda: self.stack.setCurrentWidget(self.GraphPage))
            func_menu.addAction(self.util.dict_language[self.lang]['menu_cd'], lambda: self.stack.setCurrentWidget(self.CalmDisturbPage))
            func_menu.addAction(self.util.dict_language[self.lang]['menu_c'], lambda: self.stack.setCurrentWidget(self.CalmPage))
            func_menu.addAction(self.util.dict_language[self.lang]['menu_ucd'], lambda: self.stack.setCurrentWidget(self.UniversalCDPage))

            # menu de configurações
            self.config_menu = QMenu(self.util.dict_language[self.lang]["menu_config"], self.root)
            lang_menu = QMenu(self.util.dict_language[self.lang]["menu_lang"], self.root)
            lang_menu.addAction(self.util.dict_language[self.lang]["menu_en"], lambda: self.reset("en"))
            lang_menu.addAction(self.util.dict_language[self.lang]["menu_port"], lambda: self.reset("br"))
            self.config_menu.addMenu(lang_menu)

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
            self.config_menu.addMenu(date_menu)

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
            self.config_menu.addMenu(drive_menu)

            # Exemplo: ação ao trocar drive
            drive_combo.currentTextChanged.connect(lambda: self.util.change_drive(drive_combo.currentText()))

            self.regioes_menu = QMenu(self.util.dict_language[self.lang]["menu_regiao"], self.root)
            regioes_padrao = ["mundo", "america_do_norte", "america_do_sul", "africa", "europa", "asia", "oceania"]
            for regiao in regioes_padrao:
                self.regioes_menu.addAction(self.util.dict_language[self.lang][regiao], lambda re=regiao: self.setRegiao(re))

            dados = self.util.get_region()
            regioes_diff = {}
            for dado in dados:
                if dado[0] not in regioes_padrao:
                    regioes_diff[dado[0]] = dado[1]
            for regiao, coordenadas in regioes_diff.items():
                self.regioes_menu.addAction(regiao, lambda: self.setRegiao(regiao))


            self.config_menu.addMenu(self.regioes_menu)

            self.config_menu.addAction(self.util.dict_language[self.lang]["menu_reset"], lambda: self.reset())

            menubar.addMenu(func_menu)
            menubar.addMenu(self.config_menu)
            menubar.addAction(self.util.dict_language[self.lang]["menu_about"], lambda: self.stack.setCurrentWidget(self.AboutPage))

            # abre página inicial
            self.stack.setCurrentWidget(self.GraphPage)

        else:
            self.InitialPage = InitialPage(self.root, self.lang)
            self.InitialPage.load_page()

            self.LicenseTopLevel = LicenseTopLevel(self.root, self.lang)

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

        return True

    '''def update_listbox_on_change(self):
        if self.year != self.util.get_year_config() or self.final != self.util.get_final_config():
            self.initialize_app()'''
    
    def create_license_TopLevel(self):
        self.LicenseTopLevel.load_page()
        self.LicenseTopLevel.bind_get_new_user_info(self.License.create_lincense_request)
        
    def insertMap(self):
        data = self.util.get_region()
        regioes_padrao = ["mundo", "america_do_norte", "america_do_sul", "africa", "europa", "asia", "oceania"]
        regioes = {}
        for dado in data:
            regioes[dado[0]] = dado[1]
        for dado in regioes.keys():
            if dado in regioes_padrao:
                continue
            elif any(regiao.text() == dado for regiao in self.regioes_menu.actions()):
                continue
            else:
                self.regioes_menu.addAction(dado, lambda: self.setRegiao(dado))
    
    def setRegiao(self, regiao):
        dados = self.util.get_region()
        regioes = {}
        for dado in dados:
            regioes[dado[0]] = dado[1]

        if regiao in regioes.keys():
            if regiao == "mundo":
                self.DownloadPage.map_widget.ax.set_global()
                self.GraphPage.map_widget.ax.set_global()
                self.CalmDisturbPage.map_widget.ax.set_global()
                self.CalmPage.map_widget.ax.set_global()
                self.UniversalCDPage.map_widget.ax.set_global()
            else:
                self.DownloadPage.map_widget.ax.set_extent(regioes[regiao])
                self.GraphPage.map_widget.ax.set_extent(regioes[regiao])
                self.CalmDisturbPage.map_widget.ax.set_extent(regioes[regiao])
                self.CalmPage.map_widget.ax.set_extent(regioes[regiao])
                self.UniversalCDPage.map_widget.ax.set_extent(regioes[regiao])

    def reset(self, lang="", *args, **kwargs):
        if lang not in ("", "en", "br"):
            lang = ""

        if lang != "":
            self.util.change_lang(lang)

        self.root.close()

        new_root = QMainWindow()
        new_root.resize(1920, 1080)
        new_root.showMaximized()
        new_root.setWindowIcon(QIcon(self.util.resource_pathGeneral('images/univap.ico')))
        app = MainControl(new_root)
        app.initialize_app()
        new_root.show()
