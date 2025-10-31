from Model.GraphPage.GraphsModule import GraphsModule
from Model.Custom.CustomPltOptions import CustomPltOptions
from General.util import Util
from datetime import datetime, timedelta
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QDate, Qt
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from scipy.interpolate import griddata

from PyQt5.QtWidgets import QMessageBox, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton


class ContourGraph(GraphsModule):
    def __init__(self, root, language):
        self.root = root
        self.lang = language
        self.util = Util()
        super().__init__(self.lang)

    def plot_contour(self, local_downloaded, stations, selected_types, bold_text, grid_graph,
                          start, end, selected_dates, data_with_stations):
        """
        Gera gráfico de contorno a partir de múltiplas estações.
        O eixo Y representa as estações (em suas latitudes).
        O eixo X representa o tempo.
        A intensidade é o valor interpolado entre as estações.
        """

        self.lcl_downloaded = local_downloaded
        self.stations = stations
        self.bold_text = bold_text
        self.grid_graph = grid_graph
        self.slct_dates = selected_dates
        self.data_with_stations = data_with_stations
        self.slct_types = selected_types

        self._original_clim = None

        self.start_date, self.end_date = self.format_dates(start, end)
        self.end_date += timedelta(days=1)
        if not self.start_date:
            return

        # obtém todos os dados necessários
        self.all_data = self.get_stations_data()
        if not self.all_data:
            return

        self.can_plot = True
        self.info_time = None

        # cálculo de médias e deltas se necessário
        for slct_type in selected_types:
            if 'd' in slct_type:
                self.add_delta_dict(slct_type)

        if 'reference' in selected_types:
            selected_types.remove('reference')
            selected_types.extend(f'{type.replace("d", "")}-reference' for type in selected_types if 'd' in type)
            self.add_reference(selected_types)

        avarage_types = self.calculate_type_averages(selected_types, stations)
        if not avarage_types:
            return

        self.add_plots(selected_types)
        self.config_graph(selected_types)
        if not self.can_plot:
            return

        plt.show()

    def add_delta_dict(self, type):
        base_type = type.replace('d', '')
        delta = self.calculate_midnight_average(base_type)

        for station, st in zip(self.stations, range(len(self.stations))):
            for day, times in self.all_data[station].items():
                for time in times:
                    date = times[time].get(base_type)
                    self.all_data[station][day][time][type] = date - delta[st] if date is not None else None
                    
    # add reference line for dH line 
    def add_reference(self, selected_types):
        for type in selected_types:
            if 'reference' in type:
                base_type = type.replace('-reference', '')
                delta = self.calculate_midnight_average_reference(base_type)
                calm_averages = self.calculate_reference(base_type)

                for station in self.stations:
                    for day, times in self.all_data[station].items():
                        for t, time in enumerate(times):
                            self.all_data[station][day][time][type] = calm_averages[t] - delta if calm_averages[t] is not None else None

    def add_plots(self, slct_types):
        try:
            import matplotlib as mpl
            from matplotlib.colors import LinearSegmentedColormap

            plt.close('all')
            self.fig, self.ax = plt.subplots()

            if isinstance(self.start_date, QDate):
                self.start_date = self.start_date.toPyDate()
            if isinstance(self.end_date, QDate):
                self.end_date = self.end_date.toPyDate()

            self.filtred_values = []
            self.current_contour = None
            self._current_cbar = None

            # cria colormap personalizado
            cores = [
                (1, 0, 0),       # vermelho
                (1, 0.5, 0),     # laranja
                (1, 1, 0),       # amarelo
                (0, 0.5, 1),     # azul claro
                (0, 0, 0.5)      # azul escuro
            ]
            cmap_custom = LinearSegmentedColormap.from_list("vermelho_laranja_amarelo_azul", cores)

            for plot_type in slct_types:
                times_all, lats_all, vals_all = [], [], []

                for station in self.stations:
                    station_code = station.split()[0]
                    if station_code not in self.data_with_stations:
                        continue

                    station_lat = float(self.data_with_stations[station_code][2])
                    if station_code not in self.all_data:
                        continue

                    for day_str, times in self.all_data[station_code].items():
                        day_date = datetime.strptime(day_str, "%d/%m/%Y").date()
                        for time_str, data_dict in times.items():
                            val = data_dict.get(plot_type)
                            if val is not None:
                                time_obj = datetime.strptime(time_str, "%H:%M").time()
                                dt = datetime.combine(day_date, time_obj)
                                times_all.append(dt)
                                lats_all.append(station_lat)
                                vals_all.append(val)
                                self.filtred_values.append(val)

                if not vals_all:
                    QMessageBox.information(
                        None,
                        self.util.dict_language[self.lang]["mgbox_error"],
                        f"Sem dados para {plot_type} no período selecionado."
                    )
                    self.can_plot = False
                    return

                times_num = mdates.date2num(times_all)
                lats_arr = np.array(lats_all, dtype=float)
                vals_arr = np.array(vals_all, dtype=float)

                time_grid = np.linspace(times_num.min(), times_num.max(), 300)
                lat_grid = np.linspace(lats_arr.min(), lats_arr.max(), max(50, len(np.unique(lats_arr))*5))
                X, Y = np.meshgrid(time_grid, lat_grid)

                if len(np.unique(lats_arr)) == 1:
                    # caso de uma estação
                    lat = np.unique(lats_arr)[0]
                    X, Y = np.meshgrid(time_grid, [lat - 0.001, lat + 0.001])
                    vals_interp = np.interp(time_grid, np.unique(times_num), np.interp(times_num, times_num, vals_arr))
                    Z = np.tile(vals_interp, (2, 1))
                else:
                    Z = griddata((times_num, lats_arr), vals_arr, (X, Y), method='cubic')

                    
                if Z is None or np.all(np.isnan(Z)):
                    Z = griddata((times_num, lats_arr), vals_arr, (X, Y), method='linear')

                if Z is None or np.all(np.isnan(Z)):
                    QMessageBox.information(
                        None,
                        self.util.dict_language[self.lang]["mgbox_error"],
                        f"Não foi possível interpolar valores para {plot_type} (poucos pontos)."
                    )
                    self.can_plot = False
                    return

                Z_masked = np.ma.masked_invalid(Z)
                contour = self.ax.contourf(X, Y, Z_masked, levels=100, cmap=cmap_custom.reversed())
                self.current_contour = contour
                # salva limites originais do contorno
                if not hasattr(self, '_original_clim') or self._original_clim is None:
                    self._original_clim = contour.get_clim()

                cbar = self.fig.colorbar(contour, ax=self.ax, orientation='vertical')
                self._current_cbar = cbar

                station_lats = []
                station_labels = []
                for station in self.stations:
                    code = station.split()[0]
                    info = self.data_with_stations.get(code, None)
                    if info:
                        station_lats.append(float(info[2]))  # latitude
                        station_labels.append(code)          # código da estação

                # opcional: ordenar por latitude
                station_lats = np.array(station_lats, dtype=float)
                order = np.argsort(station_lats)
                ordered_lats = station_lats[order]
                ordered_labels = [station_labels[i] for i in order]

                self.ax.set_yticks(ordered_lats.tolist())
                self.ax.set_yticklabels([f"{label} ({lat:.2f})" for label, lat in zip(ordered_labels, ordered_lats)])

            # função para abrir diálogo de limites
            def open_color_limits_dialog():
                dlg = QDialog()
                dlg.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)
                dlg.setWindowTitle("Ajustar limites de cor")
                layout = QVBoxLayout(dlg)

                current_vmin, current_vmax = self.current_contour.get_clim()
                lbl_min = QLabel("Valor mínimo:")
                le_min = QLineEdit(f"{current_vmin:.6g}")
                lbl_max = QLabel("Valor máximo:")
                le_max = QLineEdit(f"{current_vmax:.6g}")

                row_min = QHBoxLayout(); row_min.addWidget(lbl_min); row_min.addWidget(le_min)
                row_max = QHBoxLayout(); row_max.addWidget(lbl_max); row_max.addWidget(le_max)
                layout.addLayout(row_min)
                layout.addLayout(row_max)

                # botões
                btn_ok = QPushButton("OK")
                btn_cancel = QPushButton("Cancelar")
                btn_reset = QPushButton("Reset")
                btn_row = QHBoxLayout(); btn_row.addStretch(1)
                btn_row.addWidget(btn_ok); btn_row.addWidget(btn_cancel); btn_row.addWidget(btn_reset)
                layout.addLayout(btn_row)

                def on_ok():
                    try:
                        vmin, vmax = float(le_min.text()), float(le_max.text())
                    except ValueError:
                        return
                    if vmin < vmax:
                        self.current_contour.set_clim(vmin, vmax)
                        self._current_cbar.update_normal(self.current_contour)
                        vmin, vmax = float(le_min.text()), float(le_max.text())
                        if vmin < vmax:
                            self.current_contour.set_clim(vmin, vmax)       # atualiza contorno
                            self._current_cbar.update_normal(self.current_contour)  # atualiza cores
                            self._current_cbar.set_ticks(np.linspace(vmin, vmax, 10))  # recalcula ticks automáticos
                            self.fig.canvas.draw_idle()
                        dlg.close()

                def on_reset():
                    vmin = self._original_clim[0]
                    vmax = self._original_clim[1]
                    self.current_contour.set_clim(vmin, vmax)
                    self._current_cbar.update_normal(self.current_contour)
                    self._current_cbar.set_ticks(np.linspace(vmin, vmax, 10))
                    le_min.setText(f"{vmin:.6g}")  
                    le_max.setText(f"{vmax:.6g}")
                    self.fig.canvas.draw_idle()   
                    dlg.close()

                btn_ok.clicked.connect(on_ok)
                btn_cancel.clicked.connect(dlg.close)
                btn_reset.clicked.connect(on_reset)

                dlg.show()

            # evento de clique na colorbar
            def on_click(event):
                if event.inaxes is self._current_cbar.ax:
                    open_color_limits_dialog()

            self.fig.canvas.mpl_connect("button_press_event", on_click)

        except Exception as error:
            QMessageBox.information(
                None,
                self.util.dict_language[self.lang]["mgbox_error"],
                self.util.dict_language[self.lang]["mgbox_error_plt_st"]
            )
            self.can_plot = False
            print(error, "\nNECESSÁRIO AO MENOS DUAS ESTAÇÕES PARA CONTORNO")


    def config_graph(self, plot_type):
        # configura eixo X (tempo diário)
        self.ax.xaxis.set_major_locator(mdates.DayLocator())  
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%d'))
        self.ax.xaxis.set_minor_locator(mdates.HourLocator(interval=3))
        self.ax.tick_params(axis='x', which='minor', labelbottom=False)
        #self.fig.autofmt_xdate()
        #self.ax.xaxis.set_minor_locator(mdates.MinuteLocator(interval=30))

        self.ax.set_xlim(self.start_date, self.end_date)
        self.ax.set_xlabel('UT (Dias)')
        self.ax.set_ylabel('Latitude das Estações')
        period_str = f"{self.start_date.strftime('%d/%m/%Y')} - { (self.end_date - timedelta(days=1)).strftime('%d/%m/%Y') }"
        self.ax.set_title(f'{", ".join(plot_type)} | {period_str}')

        if self.bold_text:
            self.ax.xaxis.label.set_weight('bold')
            self.ax.yaxis.label.set_weight('bold')
            self.ax.title.set_weight('bold')
            for label in self.ax.get_xticklabels() + self.ax.get_yticklabels():
                label.set_fontweight('bold')

        if self.grid_graph:
            self.ax.grid(True, linestyle='-', alpha=1, which='major', color='black', linewidth=1)

    