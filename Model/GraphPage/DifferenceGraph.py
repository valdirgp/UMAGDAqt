from Model.GraphPage.GraphsModule import GraphsModule
from datetime import timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import re
from datetime import datetime
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QDate

class DifferenceGraph(GraphsModule):
    def __init__(self, root, language):
        self.root = root
        self.lang = language
        super().__init__(self.lang)

    # creates graph for a subtracted station in a period of time
    def plot_difference(self, local_downloaded, minuend_station, subtracted_station, selected_types, bold_text, grid_graph, start, end, selected_dates, cal_selection, data_with_stations):
        self.lcl_downloaded = local_downloaded
        self.min_station = minuend_station
        self.sub_station = subtracted_station
        self.stations = [minuend_station, subtracted_station]
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
            self.add_difference_reference(selected_types)
        
        self.add_plots(selected_types)
        self.config_graph(selected_types, ', '.join(self.stations))
        if not self.can_plot:
            return
        
        plt.show()

    # add delta in dict if it was selected
    def add_delta_dict(self, type):
        base_type = type.replace('d', '')
        delta = self.calculate_midnight_average(base_type)

        for st, station in enumerate(self.stations):
            for day, times in self.all_data[station].items():
                for time in times:
                    date = times[time].get(base_type)
                    self.all_data[station][day][time][type] = date - delta[st] if date is not None else None

    # add reference line
    def add_difference_reference(self, selected_types):
        for type in selected_types:
            if 'reference' in type:
                base_type = type.replace('-reference', '')
                delta = self.calculate_midnight_average(base_type)
                averages = self.calculate_averages(type, base_type, delta)

                for st, station in enumerate(self.stations):
                    for day, times in self.all_data[station].items():
                        for t, time in enumerate(times):
                            self.all_data[station][day][time][type] = averages[t] if averages[t] else None

    def calculate_averages(self, type, base_type, delta):
        # gets data from calm day
        all_data = {}
        for station in self.stations:
            dates = []
            for date in self.slct_dates:
                dt = datetime.combine(date, datetime.min.time()) + timedelta(hours=self.data_with_stations[station][3], minutes=self.data_with_stations[station][4])
                dates.append(dt.replace(hour=0, minute=0))
            especific_data = self.get_especific_dates(dates, station)
            all_data[station] = especific_data

        # applies dH in H value from calm day  
        for st, (station, days)  in enumerate(all_data.items()):
            for day, times in days.items():
                for time in times:
                    try:
                        all_data[station][day][time][type] = all_data.get(station, None).get(day, None).get(time, None).get(base_type, None) - delta[st]
                    except Exception:
                        all_data[station][day][time][type] = None

        # apply difference between two stations
        day_data = {}
        for day, times in all_data[self.min_station].items():
            time_data = {}
            for time in times:
                diff_values = {}
                for station in self.stations:
                    diff_values[station] = all_data.get(station, None).get(day, None).get(time, None).get(type, None)
                try:
                    difference = diff_values[self.min_station] - diff_values[self.sub_station]
                except Exception:
                    difference = None
                time_data[time] = difference
            day_data[day] = time_data

        # calculates average with acquired data
        averages = []
        time = datetime(year=2025, month=2, day=7, hour=0, minute=0)
        end_time = datetime(year=2025, month=2, day=8, hour=0, minute=0)

        while time < end_time:
            data = []
            for day in day_data.keys():
                value = day_data.get(day, None).get(f'{time.hour}:{time.minute}', None)
                if value: data.append(value)

            average = sum(data)/ len(data) if data else None
            averages.append(average)
            time += timedelta(minutes=1)
        
        return averages

    # plot the given data
    '''
    def add_plots(self, all_types):
        plt.close('all')
        self.fig, self.ax = plt.subplots()
        self.filtred_values = []
        if isinstance(self.start_date, QDate):
            self.start_date = self.start_date.toPyDate()
        if isinstance(self.end_date, QDate):
            self.end_date = self.end_date.toPyDate()
        difference = (self.end_date - self.start_date).days
        self.diff_data = {}

        for day, times in self.all_data[self.min_station].items():
            date = {}
            for time in times:
                current_data = {}
                for slct_type in all_types:
                    if 'reference' not in slct_type:
                        try:
                            data = self.all_data[self.min_station][day][time][slct_type] - self.all_data[self.sub_station][day][time][slct_type]
                        except Exception:
                            data = None
                    else:
                        data = self.all_data[self.min_station][day][time][slct_type]
                    current_data[slct_type] = data
                date[time] = current_data
            self.diff_data[day] = date

        for slct_type in all_types:
            plot_values = []
            for day, times in self.diff_data.items():
                for time in times:
                    data = self.diff_data[day][time][slct_type]
                    if data is not None: self.filtred_values.append(data)
                    plot_values.append(data)

            time = [self.start_date + timedelta(minutes=i) for i in range(difference * 1440)]
            if 'reference' in slct_type:
                self.ax.plot(time, plot_values, label=slct_type)
            else:
                self.ax.plot(time, plot_values, label=f'{self.min_station}-{self.sub_station} {slct_type}')
    '''

    def add_plots(self, all_types):
        plt.close('all')
        self.fig, self.ax = plt.subplots()
        self.filtred_values = []
        if isinstance(self.start_date, QDate):
            self.start_date = self.start_date.toPyDate()
        if isinstance(self.end_date, QDate):
            self.end_date = self.end_date.toPyDate()
        #difference = (self.end_date - self.start_date).days
        self.diff_data = {}

        # Calcula os dados de diferença por hora/minuto
        for day, times in self.all_data[self.min_station].items():
            date = {}
            for time in times:
                current_data = {}
                for slct_type in all_types:
                    if 'reference' not in slct_type:
                        try:
                            data = self.all_data[self.min_station][day][time][slct_type] - self.all_data[self.sub_station][day][time][slct_type]
                        except Exception:
                            data = None
                    else:
                        data = self.all_data[self.min_station][day][time][slct_type]
                    current_data[slct_type] = data
                date[time] = current_data
            self.diff_data[day] = date

        # Plota os dados com resolução por tempo (minuto a minuto)
        for slct_type in all_types:
            plot_values = []
            time_axis = []

            for day, times in self.diff_data.items():
                for time_str, values in times.items():
                    try:
                        hour, minute = map(int, time_str.split(':'))
                        dt = datetime.strptime(day, "%d/%m/%Y").replace(hour=hour, minute=minute)
                        data = values[slct_type]
                        if data is not None:
                            plot_values.append(data)
                            time_axis.append(dt)
                            self.filtred_values.append(data)
                    except Exception:
                        continue

            if time_axis and plot_values:
                label = f'{self.min_station}-{self.sub_station} {slct_type}' if 'reference' not in slct_type else slct_type
                self.ax.plot(time_axis, plot_values, label=label)

        self.ax.legend()



    # configure graph specifications
    '''
    def config_graph(self, plot_type, station):
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

        self.fig.canvas.mpl_connect('button_press_event', lambda event: self.create_exporter_level_top(event, plot_type, is_difference=True))
    '''

    def config_graph(self, plot_type, station):
        final_date = self.end_date - timedelta(days=1)

        # Mostrar apenas dias no eixo X (não horas)
        self.ax.xaxis.set_major_locator(mdates.DayLocator())
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%d'))

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
        self.ax.set_xlabel('Dia')
        self.ax.set_title(f'{station} {self.start_date.strftime("%d/%m/%Y")} - {final_date.strftime("%d/%m/%Y")}')
        self.ax.legend()

        if self.bold_text:
            self.ax.xaxis.label.set_weight('bold')
            self.ax.yaxis.label.set_weight('bold')
            self.ax.title.set_weight('bold')
            for label in self.ax.get_xticklabels() + self.ax.get_yticklabels():
                label.set_fontweight('bold')

        if self.grid_graph:
            self.ax.grid()

        self.fig.canvas.mpl_connect(
            'button_press_event',
            lambda event: self.create_exporter_level_top(event, plot_type, is_difference=True)
        )

