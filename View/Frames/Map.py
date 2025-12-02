from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QDialog, QLabel, 
                             QLineEdit, QCheckBox, QFormLayout, QTextEdit, 
                             QHBoxLayout, QInputDialog, QTimeEdit, 
                             QDialogButtonBox, QSpinBox)
from PyQt5.QtCore import pyqtSignal, QTime
from PyQt5.QtGui import QFont, QDoubleValidator
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from Model.Custom.CustomToolBar import CustomToolbar
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
from General.util import Util
from PyQt5.QtCore import pyqtSignal


class Map(QWidget):
    def __init__(self, root):
        super().__init__(root)
        self.util = Util()
        self.page_frame = root
        self.colors = None
        self.map_frame = None
        self.toolbar = None
        self.canvas = None

        self.scart_plots = []
        self.text_annotations = []
        self.all_locals = []

        self.saved_extent = None

    #método novo para acompanhar o nome de acordo com zooms e movements
    def update_annotations(self):
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()

        for i, coord in enumerate(self.all_locals):
            text = self.text_annotations[i]
            if xlim[0] <= coord['longitude'] <= xlim[1] and ylim[0] <= coord['latitude'] <= ylim[1]:
                text.set_visible(True)
            else:
                text.set_visible(False)
        self.canvas.draw_idle()


    # creates frame for to select stations
    def create_map(self):
        # Main layout for the map frame
        self.map_frame = QWidget(self.page_frame)
        layout = QVBoxLayout(self.map_frame)

        # Create matplotlib figure and axis with Cartopy
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(projection=ccrs.PlateCarree())
        self.fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
        for spine in self.ax.spines.values():
            spine.set_linewidth(2)

        self.ax.add_feature(cfeature.LAND)
        self.ax.add_feature(cfeature.OCEAN)
        self.ax.add_feature(cfeature.COASTLINE)
        self.ax.add_feature(cfeature.BORDERS)
        self.ax.add_feature(cfeature.RIVERS)

        # Create the canvas and toolbar for PyQt5
        self.canvas = FigureCanvas(self.fig)

        # Conecta o evento de redesenho para atualizar os nomes
        self.xlim_callback_id = self.ax.callbacks.connect('xlim_changed', lambda ax: self.update_annotations())
        self.ylim_callback_id = self.ax.callbacks.connect('ylim_changed', lambda ax: self.update_annotations())

        self.toolbar = CustomToolbar(self.canvas, self.map_frame, map_instance=self)


        # Add toolbar and canvas to the layout
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

        self.map_frame.setLayout(layout)
        self.map_frame.show()

    # creates points in the map accordingly to longitude and latitude list
    def set_station_map(self, longitude, latitude):
        current_extent = self.ax.get_extent()
        self.colors = ['red'] * len(longitude)
        self.scart = self.ax.scatter(longitude, latitude, s=50, c=self.colors, marker='8', transform=ccrs.PlateCarree())
        self.ax.set_extent(current_extent, crs=ccrs.PlateCarree())
        self.scart_plots.append(self.scart)
        self.canvas.draw()

    # creates text in given coordinates in station_locals and its name
    def set_stationsname_map(self, station_locals):
        self.all_locals = station_locals  # Salva os dados para uso posterior

        for coord in station_locals:
            text = self.ax.annotate(
                text=coord['station'],
                xy=(coord['longitude'], coord['latitude']),
                xytext=(5, 5),
                textcoords='offset points',
                ha='right',
                color='white',
                bbox=dict(boxstyle="round,pad=0.2", fc="black", alpha=0.5)
            )
            self.text_annotations.append(text)
        self.canvas.draw()


    # select all points from map
    def select_all_points(self):
        self.colors = ['lightgreen'] * len(self.all_locals)
        self.scart.set_facecolors(self.colors)
        self.canvas.draw()

    # clear all points from map
    def clear_all_points(self):
        self.colors = ['red'] * len(self.all_locals)
        self.scart.set_facecolor(self.colors)
        self.canvas.draw()

    def save_current_zoom(self):
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()

        # Cartopy usa extents = [x0, x1, y0, y1]
        self.saved_extent = [float(xlim[0]), float(xlim[1]), float(ylim[0]), float(ylim[1])]
        text, ok = QInputDialog.getText(None, "Salvar Zoom ", "Nome para a Região:")
        if ok:
            self.util.insert_region(text, self.saved_extent)
    
    def mapa_contorno(self):
        self.dadosContorno = pyqtSignal(tuple)

        # Atributos para armazenar os últimos valores digitados
        if not hasattr(self, "_ultimos_valores"):
            self._ultimos_valores = {
                "titulo": "",
                "minEscala": "",
                "maxEscala": "",
                "ticks": 0,
                "inicio": QTime(0, 0),
                "fim": QTime(0, 0),
                "intervalo": QTime(0, 0),
                "chk_nome": True,
                "chk_pontos": True
            }

        class MultiInputDialog(QDialog):
            def __init__(self, parent=None):
                super().__init__(parent)
                self.lang = Util().get_language_config()
                self.setWindowTitle(Util().dict_language[self.lang]["lbl_Contorno"])
                self.setMinimumWidth(350)

                layout = QVBoxLayout(self)
                form = QFormLayout()
                form.setSpacing(10)
                form.setContentsMargins(10, 10, 10, 10)

                font_bold = QFont()
                font_bold.setBold(True)
                font_bold.setPointSize(11)

                font_normal = QFont()
                font_normal.setPointSize(11)

                # --- Campos ---
                label0 = QLabel(Util().dict_language[self.lang]["lbl_title"])
                label0.setFont(font_bold)
                self.input0 = QLineEdit()
                self.input0.setFont(font_normal)
                self.input0.setText(self.parent()._ultimos_valores["titulo"])  # Preenche último valor
                form.addRow(label0, self.input0)

                label1 = QLabel(Util().dict_language[self.lang]["lbl_min_escala"])
                label1.setFont(font_bold)
                self.input1 = QLineEdit()
                self.input1.setFont(font_normal)
                validator = QDoubleValidator()
                validator.setBottom(-10000.0)
                validator.setTop(10000.0)
                validator.setDecimals(4)
                validator.setNotation(QDoubleValidator.StandardNotation)
                self.input1.setValidator(validator)
                self.input1.setText(str(self.parent()._ultimos_valores["minEscala"]))
                form.addRow(label1, self.input1)

                label2 = QLabel(Util().dict_language[self.lang]["lbl_max_escala"])
                label2.setFont(font_bold)
                self.input2 = QLineEdit()
                self.input2.setFont(font_normal)
                validator_max = QDoubleValidator()
                validator_max.setBottom(-100000.0)
                validator_max.setTop(100000.0)
                validator_max.setDecimals(4)
                self.input2.setValidator(validator_max)
                self.input2.setText(str(self.parent()._ultimos_valores["maxEscala"]))
                form.addRow(label2, self.input2)

                label3 = QLabel(Util().dict_language[self.lang]["lbl_ticks"])
                label3.setFont(font_bold)
                self.input3 = QSpinBox()
                self.input3.setMinimum(0)
                self.input3.setMaximum(1000)
                self.input3.setSingleStep(1)
                self.input3.setFont(font_normal)
                self.input3.setValue(self.parent()._ultimos_valores["ticks"])
                form.addRow(label3, self.input3)

                label4 = QLabel(Util().dict_language[self.lang]["lbl_hora_inicial"])
                label4.setFont(font_bold)
                self.input4 = QTimeEdit()
                self.input4.setDisplayFormat("HH:mm")
                self.input4.setFont(font_normal)
                self.input4.setTime(self.parent()._ultimos_valores["inicio"])
                form.addRow(label4, self.input4)

                label5 = QLabel(Util().dict_language[self.lang]["lbl_hora_final"])
                label5.setFont(font_bold)
                self.input5 = QTimeEdit()
                self.input5.setDisplayFormat("HH:mm")
                self.input5.setFont(font_normal)
                self.input5.setTime(self.parent()._ultimos_valores["fim"])
                form.addRow(label5, self.input5)

                label6 = QLabel(Util().dict_language[self.lang]["lbl_intervalo"])
                label6.setFont(font_bold)
                self.input6 = QTimeEdit()
                self.input6.setDisplayFormat("HH:mm")
                self.input6.setFont(font_normal)
                self.input6.setTime(self.parent()._ultimos_valores["intervalo"])
                form.addRow(label6, self.input6)

                label7 = QLabel(Util().dict_language[self.lang]["lbl_exibir_nome_estacoes"])
                label7.setFont(font_bold)
                self.input7 = QCheckBox()
                self.input7.setChecked(self.parent()._ultimos_valores["chk_nome"])
                self.input7.setFont(font_normal)
                form.addRow(label7, self.input7)

                label8 = QLabel(Util().dict_language[self.lang]["lbl_exibir_pontos_estacoes"])
                label8.setFont(font_bold)
                self.input8 = QCheckBox()
                self.input8.setChecked(self.parent()._ultimos_valores["chk_pontos"])
                self.input8.setFont(font_normal)
                form.addRow(label8, self.input8)
                layout.addLayout(form)

                buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
                buttons.setFont(font_normal)
                buttons.accepted.connect(self.accept)
                buttons.rejected.connect(self.reject)
                layout.addWidget(buttons)

        dialogo = MultiInputDialog(self)

        from General.signalbus import bus
        if dialogo.exec_():
            if (dialogo.input0.text() == "" or dialogo.input1.text() == "" or
                dialogo.input2.text() == "" or dialogo.input3.text() == "" or
                dialogo.input4.text() == "" or dialogo.input5.text() == "" or
                dialogo.input6.text() == ""):
                bus.contorno_ready.emit(None)
                return

            # Salva os valores digitados
            self._ultimos_valores = {
                "titulo": dialogo.input0.text(),
                "minEscala": float(dialogo.input1.text().replace(',', '.')),
                "maxEscala": float(dialogo.input2.text().replace(',', '.')),
                "ticks": int(dialogo.input3.text()),
                "inicio": dialogo.input4.time(),
                "fim": dialogo.input5.time(),
                "intervalo": dialogo.input6.time(),
                "chk_nome": dialogo.input7.isChecked(),
                "chk_pontos": dialogo.input8.isChecked()
            }

            bus.contorno_ready.emit(
                (self._ultimos_valores["titulo"],
                self._ultimos_valores["minEscala"],
                self._ultimos_valores["maxEscala"],
                self._ultimos_valores["ticks"],
                self._ultimos_valores["inicio"].toString("HH:mm"),
                self._ultimos_valores["fim"].toString("HH:mm"),
                self._ultimos_valores["intervalo"].toString("HH:mm"),
                self._ultimos_valores["chk_nome"],
                self._ultimos_valores["chk_pontos"])
            )
        '''else:
            bus.contorno_ready.emit(None)'''
