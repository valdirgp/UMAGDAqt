from Model.Custom.CustomttkFrame import ScrollableFrame
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QListWidget, 
    QAbstractItemView, QPushButton, QCheckBox, QDateEdit, QSizePolicy, 
    QScrollBar, QFrame, QCalendarWidget, QLineEdit, QListWidgetItem
)
from PyQt5.QtCore import QDate, Qt
import psutil
from General.util import Util


class SideOptionsUniversalCD(QWidget):
    def __init__(self, root, language, year, final, drive):
        super().__init__(root)
        self.util = Util()
        self.window = root
        self.lang = language
        self.year = year
        self.final = final
        self.drive = drive

        self.selected_calm_dates = []
        self.selected_disturb_dates = []

        self.combo_download_location = None
        self.local_downloads_function = None

        self.btn_plot_selected_function = None

    # Função de filtro
    def filter_visible_items(self):
        filter_text = self.search_input.text().lower()
        for i in range(self.list_all_stations.count()):
            item = self.list_all_stations.item(i)
            item.setHidden(filter_text not in item.text().lower())

    # Cria opções da aba Universal Calm/Disturb
    def create_Ucalmdisturb_plot_options(self):
        self.frame_side_functions_ucalmdisturb = ScrollableFrame(self.window, 255, 345)
        self.frame_side_functions_ucalmdisturb.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        #self.frame_side_functions_ucalmdisturb.setMinimumWidth(255)
        #self.frame_side_functions_ucalmdisturb.setMaximumWidth(340)
        #self.frame_side_functions_ucalmdisturb.setFixedWidth(255)
        self.frame_side_functions_ucalmdisturb.setObjectName("SideOptionsUniversalCD")

        layout = self.frame_side_functions_ucalmdisturb.inner_layout
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(8)

        # Drive selection
        lbl_drive = QLabel(self.util.dict_language[self.lang]['lbl_dr'])
        layout.addWidget(lbl_drive)

        self.combo_download_location = QComboBox()
        self.populate_combo_local()
        self.combo_download_location.currentIndexChanged.connect(self.change_local)
        layout.addWidget(self.combo_download_location)

        # campo para digitar filtro
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Filtrar estações...")
        layout.addWidget(self.search_input)

        # Station selection
        lbl_station = QLabel(self.util.dict_language[self.lang]['lbl_st'])
        layout.addWidget(lbl_station)

        self.list_all_stations = QListWidget()
        self.list_all_stations.setSelectionMode(QAbstractItemView.SingleSelection)
        layout.addWidget(self.list_all_stations)

        self.scrollbar = QScrollBar()
        self.list_all_stations.setVerticalScrollBar(self.scrollbar)

        # Conectar filtro em tempo real
        self.search_input.textChanged.connect(self.filter_visible_items)

        # Duration (start and end date)
        lbl_duration = QLabel(self.util.dict_language[self.lang]['lbl_dur'])
        layout.addWidget(lbl_duration)

        lbl_initial_date = QLabel(self.util.dict_language[self.lang]['lbl_init_dt'])
        layout.addWidget(lbl_initial_date)

        self.startdate = QDateEdit()
        self.startdate.setDisplayFormat('dd/MM/yyyy')
        self.startdate.setCalendarPopup(True)
        hoje = QDate.currentDate()
        data = QDate(self.year[2], self.year[1], self.year[0])
        self.startdate.setDate(data)
        layout.addWidget(self.startdate)

        lbl_final_date = QLabel(self.util.dict_language[self.lang]['lbl_fin_dt'])
        layout.addWidget(lbl_final_date)

        self.enddate = QDateEdit()
        self.enddate.setDisplayFormat('dd/MM/yyyy')
        self.enddate.setCalendarPopup(True)
        hoje = QDate.currentDate()
        data = QDate(self.final[2], self.final[1], self.final[0])
        self.enddate.setDate(data)
        layout.addWidget(self.enddate)

        def sync_calendar_month_year(calendar, dateedit):
            # Pega o dia atualmente selecionado no calendário
            dia = calendar.selectedDate().day()
            # Cria uma nova data com o ano/mês do QDateEdit, mantendo o dia atual do calendário
            nova_data = QDate(dateedit.date().year(), dateedit.date().month(), dia)
            calendar.setSelectedDate(nova_data)

        # Calm calendar
        lbl_calm_date = QLabel(self.util.dict_language[self.lang]['lbl_calm'])
        layout.addWidget(lbl_calm_date)

        self.cal_calm = QCalendarWidget()
        self.cal_calm.setGridVisible(True)
        hoje = QDate.currentDate()
        data = QDate(self.year[2], self.year[1], self.year[0])
        self.cal_calm.setSelectedDate(data)
        self.cal_calm.clicked.connect(lambda date: self.date_selected(date=date, selected_dates=self.selected_calm_dates, date_list=self.calm_date_list, calendar=self.cal_calm))
        self.cal_calm.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Conecta ao dateChanged do QDateEdit
        self.startdate.dateChanged.connect(lambda new_date: sync_calendar_month_year(self.cal_calm, self.startdate))
        self.calm_date_list = QListWidget()
        self.calm_date_list.setSelectionMode(QListWidget.MultiSelection)  # Permite selecionar múltiplos itens
        self.calm_date_list.itemClicked.connect(lambda item: self.remove_date_from_list(item=item, selected_dates=self.selected_calm_dates, date_list=self.calm_date_list, calendar=self.cal_calm))  # Conectar evento de clique na lista
        layout.addWidget(self.cal_calm)
        layout.addWidget(self.calm_date_list)

        # Disturb calendar
        lbl_disturb_date = QLabel(self.util.dict_language[self.lang]['lbl_disturb'])
        layout.addWidget(lbl_disturb_date)

        self.cal_disturb = QCalendarWidget()
        self.cal_disturb.setGridVisible(True)
        hoje = QDate.currentDate()
        data = QDate(self.year[2], self.year[1], self.year[0])
        self.cal_disturb.setSelectedDate(data)
        self.cal_disturb.clicked.connect(lambda date: self.date_selected(date=date, selected_dates=self.selected_disturb_dates, date_list=self.disturb_date_list, calendar=self.cal_disturb))
        self.cal_disturb.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Conecta ao dateChanged do QDateEdit
        self.startdate.dateChanged.connect(lambda new_date: sync_calendar_month_year(self.cal_disturb, self.startdate))
        self.disturb_date_list = QListWidget()
        self.disturb_date_list.setSelectionMode(QListWidget.MultiSelection)  # Permite selecionar múltiplos itens
        self.disturb_date_list.itemClicked.connect(lambda item: self.remove_date_from_list(item=item, selected_dates=self.selected_disturb_dates, date_list=self.disturb_date_list, calendar=self.cal_disturb))  # Conectar evento de clique na lista
        layout.addWidget(self.cal_disturb)
        layout.addWidget(self.disturb_date_list)

        # Clear button
        self.btn_clear_all = QPushButton(self.util.dict_language[self.lang]['btn_clr'])
        self.btn_clear_all.clicked.connect(self.clean_all)
        layout.addWidget(self.btn_clear_all)

        # Data types checkboxes (H, X, Y, Z, D, F, I, G)
        self.plot_checkboxes = {}
        data_types = ["H", "X", "Y", "Z", "D", "F", "I", "G"]

        for i in range(0, len(data_types), 2):
            row_layout = QHBoxLayout()
            for j in range(2):
                if i + j < len(data_types):
                    dtype = data_types[i + j]
                    cb = QCheckBox(dtype)
                    self.plot_checkboxes[dtype] = cb
                    row_layout.addWidget(cb)
            layout.addLayout(row_layout)

        # Plot button
        self.btn_plot_selected = QPushButton(self.util.dict_language[self.lang]['btn_confirm'])
        
        layout.addWidget(self.btn_plot_selected)

        self.frame_side_functions_ucalmdisturb.show()

    # Adiciona ou remove uma data na lista
    def add_date(self, qdate, list_type):
        if qdate not in list_type:
            list_type.append(qdate)
        else:
            list_type.remove(qdate)

    # Limpa os calendários e listas
    def clean_all(self):
        self.selected_calm_dates.clear()
        self.selected_disturb_dates.clear()
        self.cal_calm.setSelectedDate(QDate.currentDate())
        self.cal_disturb.setSelectedDate(QDate.currentDate())

    def date_selected(self, date, selected_dates, date_list, calendar):
        """
        Esse método será chamado quando uma data for clicada no QCalendarWidget.
        Ele adiciona ou remove a data da lista de datas selecionadas.
        """
        date_str = date.toString("dd/MM/yyyy")

        # Verifica se a data já está na lista
        if date in selected_dates:
            # Remove a data da lista
            selected_dates.remove(date)
            # Remove a data da lista visual (QListWidget)
            for i in range(date_list.count()):
                item = date_list.item(i)
                if item.text() == date_str:
                    date_list.takeItem(i)
                    break
        else:
            # Adiciona a data à lista de datas selecionadas
            selected_dates.append(date)
            # Adiciona a data ao QListWidget
            date_list.addItem(date_str)

        # Atualiza as datas destacadas no calendário
        self.update_calendar_selection(selected_dates, calendar)

    def remove_date_from_list(self, item, selected_dates, date_list, calendar):
        """
        Esse método será chamado quando um item for clicado na QListWidget.
        Ele remove a data clicada tanto da lista quanto do QCalendarWidget.
        """
        date_str = item.text()
        date = date_str.split("/")
        date = QDate(int(date[2]), int(date[1]), int(date[0]))

        # Remover a data da lista de datas selecionadas
        if date in selected_dates:
            selected_dates.remove(date)
            # Remover o item da QListWidget
            date_list.takeItem(date_list.row(item))

        # Atualiza o calendário para refletir a remoção
        self.update_calendar_selection(selected_dates, calendar)

    def update_calendar_selection(self, selected_dates, calendar):
        """
        Atualiza as datas selecionadas visualmente no QCalendarWidget.
        """
        from PyQt5.QtGui import QTextCharFormat, QColor
        from PyQt5.QtCore import QDate, Qt
        # Criar uma lista de QDate a partir das datas selecionadas
        #selected_qdates = [QDate.fromString(date, "dd/MM/yyyy") for date in self.selected_dates]
        selected_qdates = [date for date in selected_dates]
        # Criar um formato de texto para as datas selecionadas (cor vermelha)
        text_format = QTextCharFormat()
        text_format.setForeground(QColor(0, 128, 0))  # Define a cor do texto como vermelho

        # Criar um formato de texto normal (sem cor)
        normal_format = QTextCharFormat()

        # Iterar sobre as datas do mês visível
        first_date = calendar.selectedDate().addDays(-calendar.selectedDate().day() + 1)
        last_date = first_date.addMonths(1).addDays(-1)

        # Limpar as formatações anteriores (se necessário)
        for day in range(first_date.day(), last_date.day() + 1):
            date = QDate(first_date.year(), first_date.month(), day)
            calendar.setDateTextFormat(date, normal_format)

        # Aplicar a cor vermelha para as datas selecionadas
        for selected_date in selected_qdates:
            if first_date <= selected_date <= last_date:
                calendar.setDateTextFormat(selected_date, text_format)

    # Preenche a lista de estações
    def populate_list_options(self, listwidget, stations):
        selecionados = [item.text() for item in listwidget.selectedItems()]
        listwidget.clear()
        for st in stations:
            codigo = st.split()[0]   # pega só o código da estação (ex: "ARA")
            texto  = st              # texto completo (ex: "ARA (lat, lon, dip)")

            item = QListWidgetItem(texto)   # o que aparece na lista
            item.setData(Qt.UserRole, codigo)  # dado "oculto", só o código
            listwidget.addItem(item)
            if any(sel.startswith(codigo) for sel in selecionados):
                selecionar = listwidget.findItems(codigo, Qt.MatchContains)
                selecionar[0].setSelected(True)
                print(selecionar)
        self.filter_visible_items()
    # Preenche combobox com os discos
    def populate_combo_local(self):
        combo_list = []
        particoes = psutil.disk_partitions()
        for particao in particoes:
            combo_list.append(particao.device)
        self.combo_download_location.clear()
        self.combo_download_location.addItems(combo_list)
        if combo_list:
            self.combo_download_location.setCurrentIndex(0)

        index = self.combo_download_location.findText(self.drive)
        self.combo_download_location.setCurrentIndex(index)

    # Ao trocar o disco
    def change_local(self, index):
        if self.local_downloads_function:
            self.local_downloads_function()
