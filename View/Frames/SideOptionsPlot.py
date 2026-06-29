from Model.Custom.CustomttkFrame import ScrollableFrame
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QListWidget, QAbstractItemView,
    QPushButton, QCheckBox, QDateEdit, QSizePolicy, QScrollBar, QFrame, QListWidgetItem, 
    QLineEdit, QCalendarWidget, QFileDialog
)
from PyQt5.QtCore import QDate, Qt, QEvent
from PyQt5.QtGui import QColor, QBrush, QDoubleValidator
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
        self.selected_disturb_dates = set()

        self.btn_singleday_function = None
        self.btn_globaldays_function = None
        self.btn_manydays_function = None
        self.btn_contour_function = None
        self.btn_mapcontour_function = None
        self.local_downloads_function = None

        #self.updateMap_function = None
    # Função de filtro
    def filter_visible_items(self):
        def parse_val(text):
            try:
                if not text: return None
                return float(text.replace(',', '.'))
            except ValueError:
                return None

        try:
            lat_min = parse_val(self.lat_min.text())
            lat_max = parse_val(self.lat_max.text())
            lon_min = parse_val(self.lon_min.text())
            lon_max = parse_val(self.lon_max.text())
            dip_min = parse_val(self.dip_min.text())
            dip_max = parse_val(self.dip_max.text())
            search_text = self.search_input.text().lower()
        except AttributeError:
            # Caso os widgets ainda não tenham sido criados
            return

        for i in range(self.list_all_stations.count()):
            item = self.list_all_stations.item(i)
            txt = item.text()
            # Formato esperado: "CODE (lat, lon, dip)"
            hidden = False
            if search_text and search_text not in txt.lower():
                hidden = True

            if not hidden:
                try:
                    start = txt.find('(')
                    end = txt.find(')')
                    if start != -1 and end != -1:
                        parts = txt[start+1:end].split(',')
                        if len(parts) >= 3:
                            lat = float(parts[0])
                            lon = float(parts[1])
                            dip = float(parts[2])

                            if lat_min is not None and lat < lat_min: hidden = True
                            if lat_max is not None and lat > lat_max: hidden = True
                            if lon_min is not None and lon < lon_min: hidden = True
                            if lon_max is not None and lon > lon_max: hidden = True
                            if dip_min is not None and dip < dip_min: hidden = True
                            if dip_max is not None and dip > dip_max: hidden = True
                except ValueError:
                    pass
            item.setHidden(hidden)

    def set_filter_values(self, lat_min, lat_max, lon_min, lon_max):
        self.lat_min.blockSignals(True)
        self.lat_max.blockSignals(True)
        self.lon_min.blockSignals(True)
        self.lon_max.blockSignals(True)

        self.lat_min.setText(f"{lat_min:.2f}")
        self.lat_max.setText(f"{lat_max:.2f}")
        self.lon_min.setText(f"{lon_min:.2f}")
        self.lon_max.setText(f"{lon_max:.2f}")

        self.lat_min.blockSignals(False)
        self.lat_max.blockSignals(False)
        self.lon_min.blockSignals(False)
        self.lon_max.blockSignals(False)
        
        self.filter_visible_items()

    # creates options to create graphs
    def create_plot_options(self):
        # Reduzimos o mínimo para 200 e permitimos expandir até 380 se houver espaço
        self.frame_side_functions = ScrollableFrame(self.window, 200, 380)
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

        # Search text
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Filtrar por texto...")
        self.search_input.textChanged.connect(self.filter_visible_items)
        layout.addWidget(self.search_input)

        # Filtros Lat/Lon/Dip
        filter_layout = QVBoxLayout()
        filter_layout.setSpacing(2)

        # Latitude
        row_lat = QHBoxLayout()
        row_lat.addWidget(QLabel("Lat:"))
        self.lat_min = QLineEdit(); self.lat_min.setPlaceholderText("Min"); self.lat_min.setValidator(QDoubleValidator())
        self.lat_max = QLineEdit(); self.lat_max.setPlaceholderText("Max"); self.lat_max.setValidator(QDoubleValidator())
        row_lat.addWidget(self.lat_min); row_lat.addWidget(self.lat_max)
        filter_layout.addLayout(row_lat)

        # Longitude
        row_lon = QHBoxLayout()
        row_lon.addWidget(QLabel("Lon:"))
        self.lon_min = QLineEdit(); self.lon_min.setPlaceholderText("Min"); self.lon_min.setValidator(QDoubleValidator())
        self.lon_max = QLineEdit(); self.lon_max.setPlaceholderText("Max"); self.lon_max.setValidator(QDoubleValidator())
        row_lon.addWidget(self.lon_min); row_lon.addWidget(self.lon_max)
        filter_layout.addLayout(row_lon)

        # Dip
        row_dip = QHBoxLayout()
        row_dip.addWidget(QLabel("Dip:"))
        self.dip_min = QLineEdit(); self.dip_min.setPlaceholderText("Min"); self.dip_min.setValidator(QDoubleValidator())
        self.dip_max = QLineEdit(); self.dip_max.setPlaceholderText("Max"); self.dip_max.setValidator(QDoubleValidator())
        row_dip.addWidget(self.dip_min); row_dip.addWidget(self.dip_max)
        filter_layout.addLayout(row_dip)

        layout.addLayout(filter_layout)

        # Conectar sinais
        for w in [self.lat_min, self.lat_max, self.lon_min, self.lon_max, self.dip_min, self.dip_max]:
            w.textChanged.connect(self.filter_visible_items)

        # Station selection
        lbl_station = QLabel(self.util.dict_language[self.language]['lbl_st'])
        layout.addWidget(lbl_station)
        self.list_all_stations = QListWidget()
        self.list_all_stations.setSelectionMode(QAbstractItemView.SingleSelection) # Já definido como SingleSelection para o caso 10, mas é bom ter um default
        self.list_all_stations.itemSelectionChanged.connect(self.on_station_selection_changed)
        layout.addWidget(self.list_all_stations)
        self.scrollbar = QScrollBar()
        self.list_all_stations.setVerticalScrollBar(self.scrollbar)


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
        self.combo_type_plot.addItems([
        "",                                                                 #0
            self.util.dict_language[self.language]['combo_sing'],           #1
            self.util.dict_language[self.language]['combo_sing_many'],      #2
            self.util.dict_language[self.language]['combo_many'],           #3
            self.util.dict_language[self.language]['combo_tide'],           #4
            self.util.dict_language[self.language]['combo_calm_disturb'],   #5
            self.util.dict_language[self.language]['combo_calm'],           #6
            self.util.dict_language[self.language]['combo_universal'],      #7
            self.util.dict_language[self.language]['combo_contorno'],       #8
            self.util.dict_language[self.language]['combo_map_contour'],    #9
            self.util.dict_language[self.language]['combo_difference'],     #10
            self.util.dict_language[self.language]['combo_electric_field'], #11
            self.util.dict_language[self.language]['combo_vertical_drift'], #12
            self.util.dict_language[self.language]['combo_rot']             #13
        ])
        self.combo_type_plot.currentIndexChanged.connect(self.change_parameters)
        # Mapeamento de índice para cor hexadecimal
        group_colors = {
            0: "#ffffff",  # Vazio
            1: "#bbdefb", 2: "#bbdefb", 3: "#bbdefb", 4: "#bbdefb",  # Grupo Azul
            5: "#ffe0b2", 6: "#ffe0b2", 7: "#ffe0b2",               # Grupo Laranja
            8: "#a5d6a7", 9: "#a5d6a7",                             # Grupo Verde
            10: "#d1c4e9", 11: "#d1c4e9", 12: "#d1c4e9"             # Grupo Roxo
        }

        # Aplicação automatizada
        for index, hex_color in group_colors.items():
            self.combo_type_plot.setItemData(
                index, 
                QBrush(QColor(hex_color)), 
                Qt.ItemDataRole.BackgroundRole
            )
        layout.addWidget(self.combo_type_plot)

        # Placeholder for dynamic options
        self.options_frame = QFrame()
        self.options_layout = QVBoxLayout(self.options_frame)
        self.options_frame.setLayout(self.options_layout)
        layout.addWidget(self.options_frame)

        # Calm days calendar
        lbl_calm = QLabel(self.util.dict_language[self.language]['lbl_calm'])
        layout.addWidget(lbl_calm)

        self.cal_calm = QCalendarWidget()
        self.cal_calm.setGridVisible(True)
        self.cal_calm.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        data = QDate(self.year[2], self.year[1], self.year[0])
        self.cal_calm.setSelectedDate(data)
        self.cal_calm.setEnabled(False)
        for child in self.cal_calm.findChildren(QWidget):
            child.installEventFilter(self)
        self.cal_calm.clicked.connect(lambda date: self.date_selected(date, self.selected_dates, self.date_list, self.cal_calm))  # Conectar o evento de clique ao método
        layout.addWidget(self.cal_calm)

        # Lista para exibir as datas selecionadas
        self.date_list = QListWidget()
        self.date_list.setSelectionMode(QListWidget.MultiSelection)  # Permite selecionar múltiplos itens
        self.date_list.itemClicked.connect(lambda item: self.remove_date_from_list(item, self.selected_dates, self.date_list, self.cal_calm))  # Conectar evento de clique na lista
        layout.addWidget(self.date_list)

        # Botões para adicionar e remover datas diretamente da lista
        btn_layout = QHBoxLayout()
        self.btn_clear = QPushButton(self.util.dict_language[self.language]['btn_clr'])
        self.btn_clear.clicked.connect(lambda: self.clear_selection(self.cal_calm, self.date_list, self.selected_dates))
        btn_layout.addWidget(self.btn_clear)
        layout.addLayout(btn_layout)

        self.frame_side_functions.show()

    def on_checkbox_changed(self):
        """Método chamado toda vez que uma checkbox muda de estado."""
        d_checked = any(
            cb.isChecked() for lbl, cb in self.checkboxes.items() if lbl.startswith('d')
        )

        if self.combo_type_plot.currentIndex() != 0:
            if self.combo_type_plot.currentIndex() in [6, 7, 8]:
                self.cal_calm.setEnabled(True)
            else:
                self.cal_calm.setEnabled(d_checked)
        else:
            self.cal_calm.setEnabled(False)
    
    def create_none_options(self):
        self.clear_options_frame()
    
    def date_selected(self, date, selected_dates, date_list, calendar):
        """
        Esse método será chamado quando uma data for clicada no QCalendarWidget.
        Ele adiciona ou remove a data da lista de datas selecionadas.
        """
        date_str = date.toString("dd/MM/yyyy")

        if date in selected_dates:
            selected_dates.remove(date)
            for i in range(date_list.count()):
                item = date_list.item(i)
                if item.text() == date_str:
                    date_list.takeItem(i)
                    break
        else:
            # Adiciona a data à lista de datas selecionadas
            selected_dates.add(date)
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

        if date in selected_dates:
            selected_dates.remove(date)
            date_list.takeItem(date_list.row(item))
        self.update_calendar_selection(selected_dates, calendar)


    def update_calendar_selection(self, selected_dates, calendar):
        """
        Atualiza as datas selecionadas visualmente no QCalendarWidget.
        """
        from PyQt5.QtGui import QTextCharFormat, QColor
        from PyQt5.QtCore import QDate, Qt
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

    def clear_selection(self, calendar, date_list, selected_dates):
        """
        Limpa todas as datas selecionadas, tanto no calendário quanto na lista.
        """
        selected_dates.clear()  # Limpa o conjunto de datas selecionadas
        date_list.clear()  # Limpa a lista visível no QListWidget
        self.update_calendar_selection(selected_dates, calendar)  # Atualiza o calendário (desmarcando todas as datas)

    def sync_calendar_month_year(self, calendar, dateedit):
            dia = calendar.selectedDate().day()
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
        self.startdate.installEventFilter(self)
        for child in self.startdate.findChildren(QWidget):
            child.installEventFilter(self)
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
        self.startdate.installEventFilter(self)
        for child in self.startdate.findChildren(QWidget):
            child.installEventFilter(self)

        lbl_final_date = QLabel(self.util.dict_language[self.language]['lbl_fin_dt'])
        self.options_layout.addWidget(lbl_final_date)
        self.enddate = QDateEdit()
        self.enddate.setDisplayFormat('dd/MM/yyyy')
        self.enddate.setCalendarPopup(True)
        hoje = QDate.currentDate()
        data = QDate(self.final[2], self.final[1], self.final[0])
        self.enddate.setDate(data)
        self.options_layout.addWidget(self.enddate)
        self.enddate.installEventFilter(self)
        for child in self.enddate.findChildren(QWidget):
            child.installEventFilter(self)

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
        self.startdate.installEventFilter(self)
        for child in self.startdate.findChildren(QWidget):
            child.installEventFilter(self)

        lbl_final_date = QLabel(self.util.dict_language[self.language]['lbl_fin_dt'])
        self.options_layout.addWidget(lbl_final_date)
        self.enddate = QDateEdit()
        self.enddate.setDisplayFormat('dd/MM/yyyy')
        self.enddate.setCalendarPopup(True)
        hoje = QDate.currentDate()
        data = QDate(self.final[2], self.final[1], self.final[0])
        self.enddate.setDate(data)
        self.options_layout.addWidget(self.enddate)
        self.enddate.installEventFilter(self)
        for child in self.enddate.findChildren(QWidget):
            child.installEventFilter(self)

        lbl_columns = QLabel(self.util.dict_language[self.language]['lbl_colum'])
        self.options_layout.addWidget(lbl_columns)
        self.columm_entry = QComboBox()
        self.columm_entry.setEditable(True)
        self.columm_entry.setInsertPolicy(QComboBox.NoInsert)
        self.options_layout.addWidget(self.columm_entry)

        lbl_rows = QLabel(self.util.dict_language[self.language]['lbl_row'])
        self.options_layout.addWidget(lbl_rows)
        self.row_entry = QComboBox()
        self.row_entry.setEditable(True)
        self.row_entry.setInsertPolicy(QComboBox.NoInsert)
        self.options_layout.addWidget(self.row_entry)

        self.btn_manydays_confirm = QPushButton(self.util.dict_language[self.language]['btn_confirm'])
        if self.btn_manydays_function:
            self.btn_manydays_confirm.clicked.connect(self.btn_manydays_function)
        self.options_layout.addWidget(self.btn_manydays_confirm)

        self.startdate.dateChanged.connect(lambda new_date: self.sync_calendar_month_year(self.cal_calm, self.startdate))

    def add_subtractions_widget(self):
        '''lbl_minuend = QLabel(self.util.dict_language[self.language]['lbl_minuend'])
        self.options_layout.addWidget(lbl_minuend)
        self.minuend_stations_list = QListWidget()
        self.options_layout.addWidget(self.minuend_stations_list)
        lbl_subtracted = QLabel(self.util.dict_language[self.language]['lbl_subtracted'])
        self.options_layout.addWidget(lbl_subtracted)
        self.subtracted_stations_list = QListWidget()
        self.options_layout.addWidget(self.subtracted_stations_list)'''
        #self.update_lists()

        # Minuendo com checkbox para definir o destino da seleção
        self.chk_minuend = QCheckBox(self.util.dict_language[self.language]['lbl_minuend'])
        self.chk_minuend.setChecked(True)
        self.options_layout.addWidget(self.chk_minuend)
        
        self.minuend_stations_list = QListWidget()
        self.minuend_stations_list.setMaximumHeight(40)
        self.options_layout.addWidget(self.minuend_stations_list)

        # Subtraendo com checkbox para definir o destino da seleção
        self.chk_subtrahend = QCheckBox(self.util.dict_language[self.language]['lbl_subtracted'])
        self.options_layout.addWidget(self.chk_subtrahend)
        
        self.subtracted_stations_list = QListWidget()
        self.subtracted_stations_list.setMaximumHeight(40)
        self.options_layout.addWidget(self.subtracted_stations_list)

        # Lógica para garantir que apenas uma checkbox esteja marcada por vez
        self.chk_minuend.toggled.connect(lambda checked: self.chk_subtrahend.setChecked(not checked) if checked else None)
        self.chk_subtrahend.toggled.connect(lambda checked: self.chk_minuend.setChecked(not checked) if checked else None)

    def on_station_selection_changed(self):
        selected_items = self.list_all_stations.selectedItems()
        if not selected_items:
            return
        item = selected_items[0] # No modo SingleSelection, haverá apenas um item selecionado

        # Se estivermos no modo Difference (índice 10), enviamos a estação para a lista ativa
        if self.combo_type_plot.currentIndex() == 10:
            if hasattr(self, 'chk_minuend') and self.chk_minuend.isChecked():
                self.minuend_stations_list.clear()
                self.minuend_stations_list.addItem(item.text())
                if self.minuend_stations_list.count() > 0:
                    self.minuend_stations_list.item(0).setSelected(True) # Mantém o item visualmente selecionado
            elif hasattr(self, 'chk_subtrahend') and self.chk_subtrahend.isChecked():
                self.subtracted_stations_list.clear()
                self.subtracted_stations_list.addItem(item.text())
                if self.subtracted_stations_list.count() > 0:
                    self.subtracted_stations_list.item(0).setSelected(True) # Mantém o item visualmente selecionado
    
    def add_disturbance_widget(self):
        lbl_disturb_date = QLabel(self.util.dict_language[self.language]['lbl_disturb'])
        self.options_layout.addWidget(lbl_disturb_date)
        self.cal_disturb = QCalendarWidget()
        self.cal_disturb.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        self.cal_disturb.setGridVisible(True)
        hoje = QDate.currentDate()
        data = QDate(self.year[2], self.year[1], self.year[0])
        self.cal_disturb.setSelectedDate(data)
        self.cal_disturb.installEventFilter(self)
        for child in self.cal_disturb.findChildren(QWidget):
            child.installEventFilter(self)
        #self.add_date(self.cal_disturb, self.selected_disturb_dates)
        self.cal_disturb.clicked.connect(lambda date: self.date_selected(date=date, selected_dates=self.selected_disturb_dates, date_list=self.disturb_date_list, calendar=self.cal_disturb))
        self.cal_disturb.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        def sync_calendar_month_year(calendar, dateedit):
            # Pega o dia atualmente selecionado no calendário
            dia = calendar.selectedDate().day()
            # Cria uma nova data com o ano/mês do QDateEdit, mantendo o dia atual do calendário
            nova_data = QDate(dateedit.date().year(), dateedit.date().month(), dia)
            calendar.setSelectedDate(nova_data)

        
        # Conecta ao dateChanged do QDateEdit
        self.startdate.dateChanged.connect(lambda new_date: sync_calendar_month_year(self.cal_disturb, self.startdate))
        self.disturb_date_list = QListWidget()
        self.disturb_date_list.setSelectionMode(QListWidget.MultiSelection)  # Permite selecionar múltiplos itens
        self.disturb_date_list.itemClicked.connect(lambda item: self.remove_date_from_list(item=item, selected_dates=self.selected_disturb_dates, date_list=self.disturb_date_list, calendar=self.cal_disturb))  # Conectar evento de clique na lista
        self.options_layout.addWidget(self.cal_disturb)
        self.options_layout.addWidget(self.disturb_date_list)

        # Clear all button
        self.btn_clear_all = QPushButton(self.util.dict_language[self.language]['btn_clr'])
        self.btn_clear_all.clicked.connect(lambda: self.clear_selection(self.cal_disturb, self.disturb_date_list, self.selected_disturb_dates))
        self.options_layout.addWidget(self.btn_clear_all)

    def add_timeskip_widget(self):
        self.lbl_timeskip = QLabel(self.util.dict_language[self.language]['lbl_timeskip'])
        self.txt_timeskip = QLineEdit()
        self.txt_timeskip.setText("1")
        self.options_layout.addWidget(self.lbl_timeskip)
        self.options_layout.addWidget(self.txt_timeskip)
        
        self.checkRoti = QCheckBox(self.util.dict_language[self.language]['check_roti'])
        self.options_layout.addWidget(self.checkRoti)

        self.lbl_roti_threshold = QLabel(self.util.dict_language[self.language]['lbl_roti_threshold'])
        self.txt_roti_threshold = QLineEdit()
        self.txt_roti_threshold.setText("5")
        self.options_layout.addWidget(self.lbl_roti_threshold)
        self.options_layout.addWidget(self.txt_roti_threshold)

        self.lbl_roti_threshold.setVisible(False)
        self.txt_roti_threshold.setVisible(False)

        # Connect checkbox signal
        self.checkRoti.stateChanged.connect(self.toggle_roti_options)

    
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
        self.startdate.installEventFilter(self)
        for child in self.startdate.findChildren(QWidget):
            child.installEventFilter(self)

        lbl_final_date = QLabel(self.util.dict_language[self.language]['lbl_fin_dt'])
        self.options_layout.addWidget(lbl_final_date)
        self.enddate = QDateEdit()
        self.enddate.setDisplayFormat('dd/MM/yyyy')
        self.enddate.setCalendarPopup(True)
        hoje = QDate.currentDate()
        data = QDate(self.final[2], self.final[1], self.final[0])
        self.enddate.setDate(data)
        self.options_layout.addWidget(self.enddate)
        self.enddate.installEventFilter(self)
        for child in self.enddate.findChildren(QWidget):
            child.installEventFilter(self)

        self.btn_contour_confirm = QPushButton(self.util.dict_language[self.language]['btn_confirm'])
        if self.btn_contour_function:
            self.btn_contour_confirm.clicked.connect(self.btn_contour_function)
        self.options_layout.addWidget(self.btn_contour_confirm)

        self.startdate.dateChanged.connect(lambda new_date: self.sync_calendar_month_year(self.cal_calm, self.startdate))

    def create_mapcontorno_options(self):
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
        self.startdate.installEventFilter(self)
        for child in self.startdate.findChildren(QWidget):
            child.installEventFilter(self)

        lbl_final_date = QLabel(self.util.dict_language[self.language]['lbl_fin_dt'])
        self.options_layout.addWidget(lbl_final_date)
        self.enddate = QDateEdit()
        self.enddate.setDisplayFormat('dd/MM/yyyy')
        self.enddate.setCalendarPopup(True)
        hoje = QDate.currentDate()
        data = QDate(self.final[2], self.final[1], self.final[0])
        self.enddate.setDate(data)
        self.options_layout.addWidget(self.enddate)
        self.enddate.installEventFilter(self)
        for child in self.enddate.findChildren(QWidget):
            child.installEventFilter(self)

        self.btn_mapcontour_confirm = QPushButton(self.util.dict_language[self.language]['btn_confirm'])
        if self.btn_mapcontour_function:
            self.btn_mapcontour_confirm.clicked.connect(self.btn_mapcontour_function)
        self.options_layout.addWidget(self.btn_mapcontour_confirm)

        self.startdate.dateChanged.connect(lambda new_date: self.sync_calendar_month_year(self.cal_calm, self.startdate))

    def create_eletricfield_options(self):
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
        self.startdate.installEventFilter(self)
        for child in self.startdate.findChildren(QWidget):
            child.installEventFilter(self)

        lbl_final_date = QLabel(self.util.dict_language[self.language]['lbl_fin_dt'])
        self.options_layout.addWidget(lbl_final_date)
        self.enddate = QDateEdit()
        self.enddate.setDisplayFormat('dd/MM/yyyy')
        self.enddate.setCalendarPopup(True)
        hoje = QDate.currentDate()
        data = QDate(self.final[2], self.final[1], self.final[0])
        self.enddate.setDate(data)
        self.options_layout.addWidget(self.enddate)
        self.enddate.installEventFilter(self)
        for child in self.enddate.findChildren(QWidget):
            child.installEventFilter(self)

        self.btn_select_files = QPushButton(self.util.dict_language[self.language]['btn_select_files'])
        self.btn_select_files.clicked.connect(self.open_file_dialog)
        self.options_layout.addWidget(self.btn_select_files)

        self.list_files_widget = QListWidget()
        self.list_files_widget.setMaximumHeight(100)
        self.options_layout.addWidget(self.list_files_widget)

        self.btn_globaldays_confirm = QPushButton(self.util.dict_language[self.language]['btn_confirm'])
        if self.btn_globaldays_function:
            self.btn_globaldays_confirm.clicked.connect(self.btn_globaldays_function)
        self.options_layout.addWidget(self.btn_globaldays_confirm)

        self.startdate.dateChanged.connect(lambda new_date: self.sync_calendar_month_year(self.cal_calm, self.startdate))

    def open_file_dialog(self): 
        files, _ = QFileDialog.getOpenFileNames(self, "Selecionar Arquivos")
        if files:
            self.list_files_widget.clear()
            self.list_files_widget.addItems(files)

    def toggle_roti_options(self, state):
        is_checked = (state == Qt.Checked)
        self.lbl_roti_threshold.setVisible(is_checked)
        self.txt_roti_threshold.setVisible(is_checked)

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
                self.add_disturbance_widget()
                self.list_all_stations.setSelectionMode(QAbstractItemView.MultiSelection)

            case 6:

                self.create_manydays_options()
                self.list_all_stations.setSelectionMode(QAbstractItemView.MultiSelection)

            case 7:

                self.create_manydays_options()
                self.add_disturbance_widget()
                self.list_all_stations.setSelectionMode(QAbstractItemView.MultiSelection)

            case 8:

                self.create_contorno_options()
                self.list_all_stations.setSelectionMode(QAbstractItemView.MultiSelection)

            case 9:

                self.create_mapcontorno_options()
                self.list_all_stations.setSelectionMode(QAbstractItemView.MultiSelection)

            case 10:

                self.create_manydays_options()
                self.add_subtractions_widget()
                self.list_all_stations.setSelectionMode(QAbstractItemView.SingleSelection)

            case 11:

                self.create_eletricfield_options()
                self.list_all_stations.setSelectionMode(QAbstractItemView.MultiSelection)

            case 12:

                self.create_eletricfield_options()
                self.list_all_stations.setSelectionMode(QAbstractItemView.MultiSelection)
            
            case 13:
                self.create_manydays_options()
                self.add_timeskip_widget()
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
        self.list_all_stations.blockSignals(True)
        for i in range(self.list_all_stations.count()):
            item = self.list_all_stations.item(i)
            if not item.isHidden():
                item.setSelected(True)
        self.list_all_stations.blockSignals(False)
        self.list_all_stations.itemSelectionChanged.emit()

    # clear all station's list

    def clear_all_list(self):
        self.list_all_stations.blockSignals(True)
        for i in range(self.list_all_stations.count()):
            item = self.list_all_stations.item(i)
            if not item.isHidden():
                item.setSelected(False)
        self.list_all_stations.blockSignals(False)
        self.list_all_stations.itemSelectionChanged.emit()

    def clear_options_frame(self):
        while self.options_layout.count():
            item = self.options_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def eventFilter(self, source, event):
        # Bloqueia o scroll da roda do mouse
        if event.type() == QEvent.Wheel:
            return True
        # Bloqueia cliques do botão do meio
        if event.type() in [QEvent.MouseButtonPress, QEvent.MouseButtonRelease, QEvent.MouseButtonDblClick]:
            if event.button() == Qt.MiddleButton:
                return True
        return super().eventFilter(source, event)