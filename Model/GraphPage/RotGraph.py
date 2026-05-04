from Model.GraphPage.GraphsModule import GraphsModule
from General.util import Util
from datetime import timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QDate
from datetime import datetime, time, date
import math
import numpy as np

class RotGraph(GraphsModule):
    def __init__(self, root, language):
        self.root = root
        self.lang = language
        self.util = Util()
        super().__init__(self.lang)

    def plot_rot(self, local_downloaded, stations, selected_types, bold_text, grid_graph, start, end, selected_dates, 
                 cal_selection, data_with_stations, timeskip, checkRoti, Roti_timeskip):
        self.lcl_downloaded = local_downloaded
        self.stations = stations
        self.bold_text = bold_text
        self.grid_graph = grid_graph
        self.slct_dates = selected_dates
        self.cal_selection = cal_selection
        self.data_with_stations = data_with_stations
        self.slct_types = selected_types
        self.timeskip = timeskip
        self.checkRoti = checkRoti # True ou False
        self.Roti_timeskip = Roti_timeskip

        self.start_date, self.end_date = self.format_dates(start, end)
        self.end_date += timedelta(days=1)
        if not self.start_date: 
            return

        # gets all data needed
        self.all_data = self.get_stations_data()
        if not self.all_data: 
            return

        # organize and plot data
        self.can_plot = True
        self.info_time = None
        for slct_type in selected_types:
            if 'd' in slct_type: self.add_delta_dict(slct_type)

        if 'reference' in selected_types:
            selected_types.remove('reference')
            selected_types.extend(f'{type.replace("d", "")}-reference' for type in selected_types if 'd' in type)
            self.add_reference(selected_types)
        avarage_types = self.calculate_type_averages(selected_types, stations)
        if not avarage_types: 
            return

        self.add_plots(selected_types)
        self.config_graph(selected_types, ', '.join(self.stations))
        if not self.can_plot:
            return

        # Adaptação para PyQt5: usar CustomPltOptions normalmente, sem tk
        #self.fig.canvas.manager.toolmanager.add_tool('Graph Info', CustomPltOptions, inform_graph=lambda: self.inform_graph(selected_types, avarage_types))
        #self.fig.canvas.manager.toolbar.add_tool('Graph Info', 'io')
        plt.show()

        year_config = self.util.get_year_config()
        final_config = self.util.get_final_config()
        
        if self.start_date.day != year_config[0] or self.start_date.month != year_config[1] or self.start_date.year != year_config[2]:
            print("RotGraph - plot_rot")
            print("start_date:", self.start_date)
            print("year_config:", year_config)
            self.util.change_year([self.start_date.day, self.start_date.month, self.start_date.year])
        if self.end_date.day - 1 != final_config[0] or self.end_date.month != final_config[1] or self.end_date.year != final_config[2]:
            print("RotGraph - plot_rot")
            print("end_date:", self.end_date - timedelta(days=1))
            print("final_config:", final_config)
            self.util.change_final([self.end_date.day - 1, self.end_date.month, self.end_date.year])

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
            plt.close('all')
            self.fig, self.ax = plt.subplots()
            self.filtred_values = []
 
            if isinstance(self.start_date, QDate):
                self.start_date = self.start_date.toPyDate()
            if isinstance(self.end_date, QDate):
                self.end_date = self.end_date.toPyDate()
 
            try:
                timeskip_minutes = int(self.timeskip)
            except (ValueError, TypeError):
                QMessageBox.information(
                    None,
                    self.util.dict_language[self.lang]["mgbox_error"],
                    self.util.dict_language[self.lang]["mgbox_error_timeskip_invalid"]
                )
                self.can_plot = False
                return
            
            timeskip_delta = timedelta(minutes=timeskip_minutes)

            roti_delta = None
            if self.checkRoti:
                try:
                    roti_minutes = int(self.Roti_timeskip)
                    roti_delta = timedelta(minutes=roti_minutes)
                except (ValueError, TypeError):
                    # Se checkRoti é True, deve haver um valor.
                    # O controle de erro já deve ter ocorrido na UI ou usa-se um default.
                    roti_delta = timedelta(minutes=5) # Default fallback
 
            for plot_type in slct_types:
                control_reference = True
                for station in self.stations:
                    
                    station_data_flat = {
                        datetime.combine(datetime.strptime(day_str, "%d/%m/%Y").date(), datetime.strptime(time_str, "%H:%M").time()): data_dict.get(plot_type)
                        for day_str, times in self.all_data[station].items()
                        for time_str, data_dict in times.items()
                    }
 
                    if 'reference' in plot_type:
                        if control_reference:
                            x_vals = sorted(station_data_flat.keys())
                            y_vals = [station_data_flat[t] for t in x_vals]
                            self.ax.plot(x_vals, y_vals, label=plot_type)
                            self.filtred_values.extend([v for v in y_vals if v is not None])
                        control_reference = False
                        break
                    
                    # 1. Calculate ROT values for the entire period
                    rot_data = {}
                    sorted_times = sorted(station_data_flat.keys())
                    for dt_current in sorted_times:
                        dt_future = dt_current + timeskip_delta
                        val_current = station_data_flat.get(dt_current)
                        val_future = station_data_flat.get(dt_future)

                        if val_current is not None and val_future is not None:
                            rot_data[dt_current] = val_current - val_future
                        else:
                            rot_data[dt_current] = None

                    # 2. Plot ROT or ROTI
                    if not self.checkRoti:  # Plot ROT
                        x_vals = list(rot_data.keys())
                        y_vals = list(rot_data.values())
                        self.ax.plot(x_vals, y_vals, label=f'{station}-{plot_type}')
                        self.filtred_values.extend([v for v in y_vals if v is not None])
                    else:  # Plot ROTI
                        x_roti = []
                        y_roti = []
                        
                        sorted_rot_data = sorted(rot_data.items())

                        for i, (dt_current, _) in enumerate(sorted_rot_data):
                            window_end_time = dt_current + roti_delta
                            
                            # Collect ROT values within the window [dt_current, window_end_time)
                            rot_in_window = []
                            j = i
                            while j < len(sorted_rot_data) and sorted_rot_data[j][0] < window_end_time:
                                rot_val = sorted_rot_data[j][1]
                                if rot_val is not None:
                                    rot_in_window.append(rot_val)
                                j += 1

                            x_roti.append(dt_current)
                            if len(rot_in_window) > 1:
                                # Usando np.std com ddof=0 para calcular o desvio padrão populacional,
                                # que corresponde à fórmula ROTI = sqrt(<ROT²> - <ROT>²).
                                roti_val = np.std(rot_in_window, ddof=0)
                                y_roti.append(roti_val)
                                self.filtred_values.append(roti_val)
                            else:
                                y_roti.append(None)

                        self.ax.plot(x_roti, y_roti, label=f'{station}-ROTI')
                    
        except Exception as error:
            QMessageBox.information(
                None,
                self.util.dict_language[self.lang]["mgbox_error"],
                self.util.dict_language[self.lang]["mgbox_error_plt"]
            )
            self.can_plot = False
            print(error)

    # configure graph especifications
    def config_graph(self, plot_type, station):
        # Converter apenas se for QDate
        if isinstance(self.start_date, QDate):
            self.start_date = self.start_date.toPyDate()
        else:
            self.start_date = self.start_date

        if isinstance(self.end_date, QDate):
            self.end_date = self.end_date.toPyDate()
        else:
            self.end_date = self.end_date
        final_date = self.end_date - timedelta(days=1)
        timeday = [self.start_date + timedelta(days=i) for i in range((self.end_date - self.start_date).days+1)]
        self.ax.set_xticks(timeday, minor=False)
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter(f'%d'))
        self.ax.xaxis.set_minor_locator(mdates.HourLocator(interval = 3))
        self.ax.xaxis.set_minor_formatter(mdates.DateFormatter(f'%H:%M'))

        self.ax.tick_params(axis='x', which='both', top=True, labeltop=False, bottom=True, labelbottom=True)
        self.ax.tick_params(axis='x', which='minor', labelrotation=45)
        self.ax.tick_params(axis='y', which='both', right=True, labelright=False, left=True, labelleft=True)

        self.ax.set_xlim(self.start_date, self.end_date)
        valid_values = [v for v in self.filtred_values if v is not None and not math.isnan(v) and not math.isinf(v)]
        if valid_values:
            all_problems = set(getattr(self, 'problematic_data', []) + getattr(self, 'problematic_calm_days', []))
            if all_problems:
                msg = self.util.dict_language[self.lang]["mgbox_error_noinfo_period"] + ":\n" + "\n".join(all_problems)
                QMessageBox.warning(None, self.util.dict_language[self.lang]["lbl_warn"], msg)
            self.ax.set_ylim(min(valid_values), max(valid_values))
        else:
            QMessageBox.information(
                None,
                self.util.dict_language[self.lang]["mgbox_error"],
                self.util.dict_language[self.lang]["mgbox_error_noinfo_period"]
            )
            self.can_plot = False
            return

        self.ax.set_ylabel(f'{", ".join(plot_type)} ({self.get_measure(plot_type)})')
        self.ax.set_xlabel('UT')
        self.ax.set_title(f'{station} {self.start_date.day:02}/{self.start_date.month:02}/{self.start_date.year} - {final_date.day:02}/{final_date.month:02}/{final_date.year}')
        self.ax.legend()

        if self.bold_text:
            self.ax.xaxis.label.set_weight('bold')
            self.ax.yaxis.label.set_weight('bold')
            self.ax.title.set_weight('bold')
            for label in self.ax.get_xticklabels() + self.ax.get_yticklabels():
                label.set_fontweight('bold')

        if self.grid_graph:
            self.ax.grid()
            self.ax.grid(which='minor', linestyle='--', linewidth=0.5)

        if self.checkRoti:
            self.fig.canvas.mpl_connect('button_press_event', lambda event: self.create_exporter_level_top(event, "ROTI - dH"))
        else:
            self.fig.canvas.mpl_connect('button_press_event', lambda event: self.create_exporter_level_top(event, "ROT - dH"))