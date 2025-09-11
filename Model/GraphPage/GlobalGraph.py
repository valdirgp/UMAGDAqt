from Model.GraphPage.GraphsModule import GraphsModule
from Model.Custom.CustomPltOptions import CustomPltOptions
from datetime import timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QDate
from datetime import datetime

class GlobalGraph(GraphsModule):
    def __init__(self, root, language):
        self.root = root
        self.lang = language
        super().__init__(self.lang)

    # creates one graph that has all data in a period of time
    def plot_global_days(self, local_downloaded, stations, selected_types, bold_text, grid_graph, start, end, selected_dates, cal_selection, data_with_stations):
        self.lcl_downloaded = local_downloaded
        self.stations = stations
        self.bold_text = bold_text
        self.grid_graph = grid_graph
        self.slct_dates = selected_dates
        self.cal_selection = cal_selection
        self.data_with_stations = data_with_stations
        self.slct_types = selected_types

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
        self.fig.canvas.manager.toolmanager.add_tool('Graph Info', CustomPltOptions, inform_graph=lambda: self.inform_graph(selected_types, avarage_types))
        self.fig.canvas.manager.toolbar.add_tool('Graph Info', 'io')
        plt.show()

    # add delta in dict if it was selected
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

    '''# plot the given data
    def add_plots(self, slct_types):
        try:    
            plt.close('all')
            plt.rcParams['toolbar'] = 'toolmanager' # allows custom tools mode
            self.fig, self.ax = plt.subplots()
            self.filtred_values = []
            if isinstance(self.start_date, QDate):
                self.start_date = self.start_date.toPyDate()
            if isinstance(self.end_date, QDate):
                self.end_date = self.end_date.toPyDate()
            difference = (self.end_date - self.start_date).days

            for plot_type in slct_types:
                control_reference = True
                for station in self.stations:
                    plot_values = []
                    for day, times in self.all_data[station].items():
                        for time in times:
                            data = self.all_data[station][day][time][plot_type]
                            if data is not None: self.filtred_values.append(data)
                            plot_values.append(data)    
                    time = [self.start_date + timedelta(minutes=i) for i in range(difference * 1440)]
                    if 'reference' in plot_type:
                        if control_reference: # controle para que o mesmo tipo de referencia não se repita
                            self.ax.plot(time, plot_values, label=plot_type)
                        break
                    else:
                        self.ax.plot(time, plot_values, label=f'{station}-{plot_type}')
                    control_reference = False

        except Exception as error:
            QMessageBox.information(
                None,
                self.util.dict_language[self.lang]["mgbox_error"],
                self.util.dict_language[self.lang]["mgbox_error_plt"]
            )
            self.can_plot = False
            print(error)'''
    
    def add_plots(self, slct_types):
        try:
            plt.close('all')
            plt.rcParams['toolbar'] = 'toolmanager'
            self.fig, self.ax = plt.subplots()
            self.filtred_values = []

            if isinstance(self.start_date, QDate):
                self.start_date = self.start_date.toPyDate()
            if isinstance(self.end_date, QDate):
                self.end_date = self.end_date.toPyDate()

            for plot_type in slct_types:
                control_reference = True
                for station in self.stations:
                    x_vals = []
                    
                    y_vals = []
                    for day_str, times in self.all_data[station].items():
                        day_date = datetime.strptime(day_str, "%d/%m/%Y").date()
                        for time_str, data_dict in times.items():
                            val = data_dict.get(plot_type)
                            if val is not None:
                                # Combina a data com a hora para ter datetime completo
                                time_obj = datetime.strptime(time_str, "%H:%M").time()
                                dt = datetime.combine(day_date, time_obj)
                                x_vals.append(dt)
                                y_vals.append(val)
                                self.filtred_values.append(val)

                    # Ordena os pontos para garantir que estão em ordem temporal
                    sorted_pairs = sorted(zip(x_vals, y_vals))
                    x_sorted, y_sorted = zip(*sorted_pairs) if sorted_pairs else ([], [])

                    if 'reference' in plot_type:
                        if control_reference:
                            self.ax.plot(x_sorted, y_sorted, label=plot_type)
                        break
                    else:
                        self.ax.plot(x_sorted, y_sorted, label=f'{station}-{plot_type}')
                    control_reference = False

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

        self.ax.tick_params(axis='x', which='both', top=True, labeltop=False, bottom=True, labelbottom=True)
        self.ax.tick_params(axis='y', which='both', right=True, labelright=False, left=True, labelleft=True)

        self.ax.set_xlim(self.start_date, self.end_date)
        if self.filtred_values:
            self.ax.set_ylim(min(self.filtred_values), max(self.filtred_values))
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

        self.fig.canvas.mpl_connect('button_press_event', lambda event: self.create_exporter_level_top(event, plot_type))