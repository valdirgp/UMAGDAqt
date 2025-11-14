from Model.Custom.CustomttkFrame import ScrollableFrame
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QListWidget, QAbstractItemView,
    QPushButton, QCheckBox, QDateEdit, QSizePolicy, QScrollBar, QFrame, QListWidgetItem, 
    QLineEdit, QCalendarWidget
)
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtGui import QWheelEvent
import psutil
from General.util import Util

class SideOptionsPlot(QWidget):
    def __init__(self, root, language, year, final, drive):
        super().__init__(root)
        self.util = Util()
        self.window = root
        self.language = language
        self.year = year
        self.final = final
        self.drive = drive
        self.selected_dates = set()

        self.btn_singleday_function = None
        self.btn_globaldays_function = None
        self.btn_manydays_function = None
        self.btn_contour_function = None
        self.local_downloads_function = None

        #self.updateMap_function = None

        self.selected_dates = set()

    # Função de filtro
    def filter_visible_items(self):
        filter_text = self.search_input.text().lower()
        for i in range(self.list_all_stations.count()):
            item = self.list_all_stations.item(i)
            item.setHidden(filter_text not in item.text().lower())

    # creates options to create graphs
    def create_plot_options(self):
        self.frame_side_functions = ScrollableFrame(self.window, 255, 330)
        self.frame_side_functions.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.frame_side_functions.setObjectName("sideOptionsPlotFrame")

        #layout = QVBoxLayout(self.frame_side_functions.inner_frame)
        layout = self.frame_side_functions.inner_layout   # usa o já criado no ScrollableFrame
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(8)

        # Drive selection
        lbl_drive = QLabel(self.util.dict_language[self.language]['lbl_dr'])
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
        lbl_station = QLabel(self.util.dict_language[self.language]['lbl_st'])
        layout.addWidget(lbl_station)
        self.list_all_stations = QListWidget()
        self.list_all_stations.setSelectionMode(QAbstractItemView.MultiSelection)
        layout.addWidget(self.list_all_stations)
        self.scrollbar = QScrollBar()
        self.list_all_stations.setVerticalScrollBar(self.scrollbar)

        # Conectar filtro em tempo real
        self.search_input.textChanged.connect(self.filter_visible_items)

        # Select/Clear all buttons
        btns_layout = QHBoxLayout()
        self.btn_select_all = QPushButton(self.util.dict_language[self.language]['btn_slt'])
        self.btn_select_all.clicked.connect(self.select_all_list)
        btns_layout.addWidget(self.btn_select_all)
        self.btn_clear_all = QPushButton(self.util.dict_language[self.language]['btn_clr'])
        self.btn_clear_all.clicked.connect(self.clear_all_list)
        btns_layout.addWidget(self.btn_clear_all)
        layout.addLayout(btns_layout)

        # Plot options
        lbl_plot_opts = QLabel(self.util.dict_language[self.language]['lbl_plt'])
        layout.addWidget(lbl_plot_opts)

        # Plot type checkboxes
        self.checkboxes = {}
        plot_types = [
            ('dH', 'is_dH'), ('H', 'is_H'),
            ('dD', 'is_dD'), ('D', 'is_D'),
            ('dZ', 'is_dZ'), ('Z', 'is_Z'),
            ('dI', 'is_dI'), ('I', 'is_I'),
            ('dF', 'is_dF'), ('F', 'is_F'),
            ('dG', 'is_dG'), ('G', 'is_G'),
            ('dX', 'is_dX'), ('X', 'is_X'),
            ('dY', 'is_dY'), ('Y', 'is_Y'),
            ('Reference', 'is_reference')
        ]
        for i in range(0, len(plot_types), 2):
            row_layout = QHBoxLayout()
            for j in range(2):
                if i + j < len(plot_types):
                    label, attr = plot_types[i + j]
                    cb = QCheckBox(label)
                    setattr(self, attr, cb)
                    self.checkboxes[label] = cb
                    cb.stateChanged.connect(self.on_checkbox_changed)
                    row_layout.addWidget(cb)
            layout.addLayout(row_layout)

        # Graph options
        lbl_graph_opts = QLabel(self.util.dict_language[self.language]['lbl_graph_opts'])
        layout.addWidget(lbl_graph_opts)
        row_opts = QHBoxLayout()
        self.is_bold_text = QCheckBox(self.util.dict_language[self.language]['check_bold'])
        row_opts.addWidget(self.is_bold_text)
        self.is_grid_graph = QCheckBox(self.util.dict_language[self.language]['check_grid'])
        row_opts.addWidget(self.is_grid_graph)
        layout.addLayout(row_opts)

        # Graph type selection
        lbl_tpgraph = QLabel(self.util.dict_language[self.language]['lbl_tpgraph'])
        layout.addWidget(lbl_tpgraph)
        self.combo_type_plot = QComboBox()
        self.combo_type_plot.setMaximumWidth(310)
        self.combo_type_plot.addItems([
            "",
            self.util.dict_language[self.language]['combo_sing'],
            self.util.dict_language[self.language]['combo_sing_many'],
            self.util.dict_language[self.language]['combo_many'],
            self.util.dict_language[self.language]['combo_tide'],
            self.util.dict_language[self.language]['combo_difference'],
            self.util.dict_language[self.language]['combo_contorno']
        ])
        self.combo_type_plot.currentIndexChanged.connect(self.change_parameters)
        layout.addWidget(self.combo_type_plot)

        # Placeholder for dynamic options
        self.options_frame = QFrame()
        self.options_layout = QVBoxLayout(self.options_frame)
        self.options_frame.setLayout(self.options_layout)
        #self.create_oneday_options()
        layout.addWidget(self.options_frame)

        # Calm days calendar
        lbl_calm = QLabel(self.util.dict_language[self.language]['lbl_calm'])
        layout.addWidget(lbl_calm)

        self.cal_calm = QCalendarWidget()
        self.cal_calm.setMaximumWidth(320)
        self.cal_calm.setGridVisible(True)
        self.cal_calm.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        data = QDate(self.year[2], self.year[1], self.year[0])
        self.cal_calm.setSelectedDate(data)
        self.cal_calm.setEnabled(False)
        self.cal_calm.clicked.connect(self.date_selected)  # Conectar o evento de clique ao método
        layout.addWidget(self.cal_calm)

        # Lista para exibir as datas selecionadas
        self.date_list = QListWidget()
        self.date_list.setMaximumWidth(310)
        self.date_list.setSelectionMode(QListWidget.MultiSelection)  # Permite selecionar múltiplos itens
        self.date_list.itemClicked.connect(self.remove_date_from_list)  # Conectar evento de clique na lista
        layout.addWidget(self.date_list)

        # Botões para adicionar e remover datas diretamente da lista
        btn_layout = QHBoxLayout()
        self.btn_clear = QPushButton("Limpar Seleção")
        self.btn_clear.clicked.connect(self.clear_selection)
        btn_layout.addWidget(self.btn_clear)
        layout.addLayout(btn_layout)

        #self.frame_side_functions.inner_frame.setLayout(layout)
        #self.frame_side_functions.setLayout(QVBoxLayout())
        self.frame_side_functions.show()

    def on_checkbox_changed(self):
        """Método chamado toda vez que uma checkbox muda de estado."""
        d_checked = any(
            cb.isChecked() for lbl, cb in self.checkboxes.items() if lbl.startswith('d')
        )

        if self.combo_type_plot.currentIndex() not in (0, 5):
            self.cal_calm.setEnabled(d_checked)
        else:
            self.cal_calm.setEnabled(False)
    
    def create_none_options(self):
        self.clear_options_frame()
    
    def date_selected(self, date):
        """
        Esse método será chamado quando uma data for clicada no QCalendarWidget.
        Ele adiciona ou remove a data da lista de datas selecionadas.
        """
        date_str = date.toString("dd/MM/yyyy")

        # Verifica se a data já está na lista
        if date in self.selected_dates:
            # Remove a data da lista
            self.selected_dates.remove(date)
            # Remove a data da lista visual (QListWidget)
            for i in range(self.date_list.count()):
                item = self.date_list.item(i)
                if item.text() == date_str:
                    self.date_list.takeItem(i)
                    break
        else:
            # Adiciona a data à lista de datas selecionadas
            self.selected_dates.add(date)
            # Adiciona a data ao QListWidget
            self.date_list.addItem(date_str)

        # Atualiza as datas destacadas no calendário
        self.update_calendar_selection()

    def remove_date_from_list(self, item):
        """
        Esse método será chamado quando um item for clicado na QListWidget.
        Ele remove a data clicada tanto da lista quanto do QCalendarWidget.
        """
        date_str = item.text()
        date = date_str.split("/")
        date = QDate(int(date[2]), int(date[1]), int(date[0]))

        # Remover a data da lista de datas selecionadas
        if date in self.selected_dates:
            self.selected_dates.remove(date)
            # Remover o item da QListWidget
            self.date_list.takeItem(self.date_list.row(item))

        # Atualiza o calendário para refletir a remoção
        self.update_calendar_selection()

    def update_calendar_selection(self):
        """
        Atualiza as datas selecionadas visualmente no QCalendarWidget.
        """
        from PyQt5.QtGui import QTextCharFormat, QColor
        from PyQt5.QtCore import QDate, Qt
        # Criar uma lista de QDate a partir das datas selecionadas
        #selected_qdates = [QDate.fromString(date, "dd/MM/yyyy") for date in self.selected_dates]
        selected_qdates = [date for date in self.selected_dates]
        # Criar um formato de texto para as datas selecionadas (cor vermelha)
        text_format = QTextCharFormat()
        text_format.setForeground(QColor(0, 128, 0))  # Define a cor do texto como vermelho

        # Criar um formato de texto normal (sem cor)
        normal_format = QTextCharFormat()

        # Iterar sobre as datas do mês visível
        first_date = self.cal_calm.selectedDate().addDays(-self.cal_calm.selectedDate().day() + 1)
        last_date = first_date.addMonths(1).addDays(-1)

        # Limpar as formatações anteriores (se necessário)
        for day in range(first_date.day(), last_date.day() + 1):
            date = QDate(first_date.year(), first_date.month(), day)
            self.cal_calm.setDateTextFormat(date, normal_format)

        # Aplicar a cor vermelha para as datas selecionadas
        for selected_date in selected_qdates:
            if first_date <= selected_date <= last_date:
                self.cal_calm.setDateTextFormat(selected_date, text_format)

    def clear_selection(self):
        """
        Limpa todas as datas selecionadas, tanto no calendário quanto na lista.
        """
        self.selected_dates.clear()  # Limpa o conjunto de datas selecionadas
        self.date_list.clear()  # Limpa a lista visível no QListWidget
        self.update_calendar_selection()  # Atualiza o calendário (desmarcando todas as datas)

    def sync_calendar_month_year(self, calendar, dateedit):
            # Pega o dia atualmente selecionado no calendário
            dia = calendar.selectedDate().day()
            # Cria uma nova data com o ano/mês do QDateEdit, mantendo o dia atual do calendário
            nova_data = QDate(dateedit.date().year(), dateedit.date().month(), dia)
            calendar.setSelectedDate(nova_data)

    # create a child for frame_side_functions to have one day options
    def create_oneday_options(self):
        self.clear_options_frame()
        lbl_date = QLabel(self.util.dict_language[self.language]['lbl_dt'])
        self.options_layout.addWidget(lbl_date)
        self.startdate = QDateEdit()
        self.startdate.setDisplayFormat('dd/MM/yyyy')
        self.startdate.setCalendarPopup(True)
        hoje = QDate.currentDate()
        data = QDate(self.year[2], self.year[1], self.year[0])
        self.startdate.setDate(data)
        self.options_layout.addWidget(self.startdate)
        self.btn_singleday_confirm = QPushButton(self.util.dict_language[self.language]['btn_confirm'])
        if self.btn_singleday_function:
            self.btn_singleday_confirm.clicked.connect(self.btn_singleday_function)
        self.options_layout.addWidget(self.btn_singleday_confirm)

        self.startdate.dateChanged.connect(lambda new_date: self.sync_calendar_month_year(self.cal_calm, self.startdate))

    # create a child for frame_side_functions to have many days options
    def create_manydays_options(self):
        self.clear_options_frame()
        lbl_initial_date = QLabel(self.util.dict_language[self.language]['lbl_init_dt'])
        self.options_layout.addWidget(lbl_initial_date)
        self.startdate = QDateEdit()
        self.startdate.setDisplayFormat('dd/MM/yyyy')
        self.startdate.setCalendarPopup(True)
        hoje = QDate.currentDate()
        data = QDate(self.year[2], self.year[1], self.year[0])
        self.startdate.setDate(data)
        self.options_layout.addWidget(self.startdate)

        lbl_final_date = QLabel(self.util.dict_language[self.language]['lbl_fin_dt'])
        self.options_layout.addWidget(lbl_final_date)
        self.enddate = QDateEdit()
        self.enddate.setDisplayFormat('dd/MM/yyyy')
        self.enddate.setCalendarPopup(True)
        hoje = QDate.currentDate()
        data = QDate(self.final[2], self.final[1], self.final[0])
        self.enddate.setDate(data)
        self.options_layout.addWidget(self.enddate)

        self.btn_globaldays_confirm = QPushButton(self.util.dict_language[self.language]['btn_confirm'])
        if self.btn_globaldays_function:
            self.btn_globaldays_confirm.clicked.connect(self.btn_globaldays_function)
        self.options_layout.addWidget(self.btn_globaldays_confirm)

        self.startdate.dateChanged.connect(lambda new_date: self.sync_calendar_month_year(self.cal_calm, self.startdate))

    # create a child for frame_side_functions to have grid options
    def create_grid_options(self):
        self.clear_options_frame()
        lbl_initial_date = QLabel(self.util.dict_language[self.language]['lbl_init_dt'])
        self.options_layout.addWidget(lbl_initial_date)
        self.startdate = QDateEdit()
        self.startdate.setDisplayFormat('dd/MM/yyyy')
        self.startdate.setCalendarPopup(True)
        hoje = QDate.currentDate()
        data = QDate(self.year[2], self.year[1], self.year[0])
        self.startdate.setDate(data)
        self.options_layout.addWidget(self.startdate)

        lbl_final_date = QLabel(self.util.dict_language[self.language]['lbl_fin_dt'])
        self.options_layout.addWidget(lbl_final_date)
        self.enddate = QDateEdit()
        self.enddate.setDisplayFormat('dd/MM/yyyy')
        self.enddate.setCalendarPopup(True)
        hoje = QDate.currentDate()
        data = QDate(self.final[2], self.final[1], self.final[0])
        self.enddate.setDate(data)
        self.options_layout.addWidget(self.enddate)

        lbl_columns = QLabel(self.util.dict_language[self.language]['lbl_colum'])
        self.options_layout.addWidget(lbl_columns)
        self.columm_entry = QComboBox()
        self.columm_entry.setEditable(True)
        self.columm_entry.setInsertPolicy(QComboBox.NoInsert)
        self.columm_entry.setMaximumWidth(310)
        self.options_layout.addWidget(self.columm_entry)

        lbl_rows = QLabel(self.util.dict_language[self.language]['lbl_row'])
        self.options_layout.addWidget(lbl_rows)
        self.row_entry = QComboBox()
        self.row_entry.setEditable(True)
        self.row_entry.setInsertPolicy(QComboBox.NoInsert)
        self.row_entry.setMaximumWidth(310)
        self.options_layout.addWidget(self.row_entry)

        self.btn_manydays_confirm = QPushButton(self.util.dict_language[self.language]['btn_confirm'])
        if self.btn_manydays_function:
            self.btn_manydays_confirm.clicked.connect(self.btn_manydays_function)
        self.options_layout.addWidget(self.btn_manydays_confirm)

        self.startdate.dateChanged.connect(lambda new_date: self.sync_calendar_month_year(self.cal_calm, self.startdate))

    def add_subtractions_widget(self):
        lbl_minuend = QLabel(self.util.dict_language[self.language]['lbl_minuend'])
        self.options_layout.addWidget(lbl_minuend)
        self.minuend_stations_list = QListWidget()
        self.minuend_stations_list.setMaximumWidth(310)
        self.options_layout.addWidget(self.minuend_stations_list)
        lbl_subtracted = QLabel(self.util.dict_language[self.language]['lbl_subtracted'])
        self.options_layout.addWidget(lbl_subtracted)
        self.subtracted_stations_list = QListWidget()
        self.subtracted_stations_list.setMaximumWidth(310)
        self.options_layout.addWidget(self.subtracted_stations_list)
        self.update_lists()
    
    def create_contorno_options(self):
        self.clear_options_frame()

        lbl_initial_date = QLabel(self.util.dict_language[self.language]['lbl_init_dt'])
        self.options_layout.addWidget(lbl_initial_date)
        self.startdate = QDateEdit()
        self.startdate.setDisplayFormat('dd/MM/yyyy')
        self.startdate.setCalendarPopup(True)
        hoje = QDate.currentDate()
        data = QDate(self.year[2], self.year[1], self.year[0])
        self.startdate.setDate(data)
        self.options_layout.addWidget(self.startdate)

        lbl_final_date = QLabel(self.util.dict_language[self.language]['lbl_fin_dt'])
        self.options_layout.addWidget(lbl_final_date)
        self.enddate = QDateEdit()
        self.enddate.setDisplayFormat('dd/MM/yyyy')
        self.enddate.setCalendarPopup(True)
        hoje = QDate.currentDate()
        data = QDate(self.final[2], self.final[1], self.final[0])
        self.enddate.setDate(data)
        self.options_layout.addWidget(self.enddate)

        self.btn_contour_confirm = QPushButton(self.util.dict_language[self.language]['btn_confirm'])
        if self.btn_contour_function:
            self.btn_contour_confirm.clicked.connect(self.btn_contour_function)
        self.options_layout.addWidget(self.btn_contour_confirm)

        self.startdate.dateChanged.connect(lambda new_date: self.sync_calendar_month_year(self.cal_calm, self.startdate))

    # changes kind of options plotting
    def change_parameters(self, index):
        match index:
            case 0:
                self.create_none_options()
                self.list_all_stations.setSelectionMode(QAbstractItemView.NoSelection)
            case 1:
                self.create_oneday_options()
                self.list_all_stations.setSelectionMode(QAbstractItemView.MultiSelection)
            case 2:
                self.create_manydays_options()
                self.list_all_stations.setSelectionMode(QAbstractItemView.MultiSelection)
            case 3:
                self.create_grid_options()
                self.list_all_stations.setSelectionMode(QAbstractItemView.MultiSelection)
            case 4:
                self.create_manydays_options()
                self.list_all_stations.setSelectionMode(QAbstractItemView.MultiSelection)
            case 5:
                self.create_manydays_options()
                self.add_subtractions_widget()
                self.list_all_stations.setSelectionMode(QAbstractItemView.NoSelection)
            case 6:
                self.create_contorno_options()
                self.list_all_stations.setSelectionMode(QAbstractItemView.MultiSelection)
        self.on_checkbox_changed()

    # update all info came from the chosen drive 
    def change_local(self, index):
        if self.local_downloads_function:
            self.local_downloads_function()
        if self.util.get_drive_config() != self.combo_download_location.currentText():
            self.util.change_drive(self.combo_download_location.currentText())
        '''if self.updateMap_function:
            self.updateMap_function()'''
        


    # fill a listbox with the given data
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
        self.filter_visible_items()

    # fill combobox that is chooses path
    def populate_combo_local(self):
        combo_list = []
        particoes = psutil.disk_partitions()
        for particao in particoes:
            combo_list.append(particao.device)
        self.combo_download_location.clear()
        self.combo_download_location.addItems(combo_list)
        if combo_list:
            #self.combo_download_location.setCurrentIndex(self.combo_download_location.findText(self.drive))
            self.combo_download_location.setCurrentIndex(0)

        index = self.combo_download_location.findText(self.drive)
        self.combo_download_location.setCurrentIndex(index)

    # select all station's list
    def select_all_list(self):
        self.list_all_stations.selectAll()

    # clear all station's list
    def clear_all_list(self):
        self.list_all_stations.clearSelection()

    def clear_options_frame(self):
        while self.options_layout.count():
            item = self.options_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()