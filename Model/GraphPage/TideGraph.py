from Model.GraphPage.GraphsModule import GraphsModule
from Model.Custom.CustomPltOptions import CustomPltOptions
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from PyQt5.QtWidgets import QMessageBox

class TideGraph(GraphsModule):
    def __init__(self, root, language):
        self.root = root
        self.lang = language
        super().__init__(self.lang, self.root)

    # creates one graph that has all data in a period of time
    def plot_tide(self, local_downloaded, stations, selected_types, bold_text, grid_graph, start, end, selected_dates, cal_selection, data_with_stations):
        self.lcl_downloaded = local_downloaded
        self.stations = stations
        self.bold_text = bold_text
        self.grid_graph = grid_graph
        self.slct_dates = selected_dates
        self.cal_selection = cal_selection
        self.data_with_stations = data_with_stations
        self.slct_types = selected_types

        self.start_date, self.end_date = self.format_dates(start, end)
        if not self.start_date:
            return
        self.end_date += timedelta(days=1)

        # gets all data needed
        self.all_data = self.get_stations_data()
        if not self.all_data:
            return

        # organize and plot data
        self.can_plot = True
        self.info_time = None
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
        self.config_graph(selected_types, ', '.join(self.stations))
        if not self.can_plot:
            return

        self.fig.canvas.manager.toolmanager.add_tool(
            'Graph Info',
            CustomPltOptions,
            inform_graph=lambda: self.inform_graph(selected_types, avarage_types)
        )
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

    # add in plot the given data
    def add_plots(self, slct_types):
        try:
            plt.close('all')
            plt.rcParams['toolbar'] = 'toolmanager'
            self.fig, self.ax = plt.subplots()
            self.filtred_values = []

            for plot_type in slct_types:
                control_reference = True
                for station in self.stations:
                    for day, times in self.all_data[station].items():
                        plot_values = []
                        for time in times:
                            data = self.all_data[station][day][time][plot_type]
                            if data is not None:
                                self.filtred_values.append(data)
                            plot_values.append(data)

                        time_axis = [self.start_date + timedelta(minutes=min) for min in range(1440)]
                        if 'reference' in plot_type:
                            if control_reference:
                                self.ax.plot(time_axis, plot_values, label=plot_type)
                            break
                        else:
                            self.ax.plot(time_axis, plot_values, label=f'{station}-{plot_type}')
                    control_reference = False

        except Exception as error:
            self.show_message(
                self.util.dict_language[self.lang]["mgbox_error"],
                self.util.dict_language[self.lang]["mgbox_error_plt"]
            )
            self.can_plot = False
            print(error)

    # configure graph specifications
    def config_graph(self, plot_type, station):
        final_date = self.end_date - timedelta(days=1)
        self.ax.minorticks_on()
        timehour = [self.start_date + timedelta(hours=i) for i in range(24)]
        self.ax.set_xticks(timehour, minor=True)
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

        self.ax.tick_params(axis='x', which='both', top=True, labeltop=False, bottom=True, labelbottom=True)
        self.ax.tick_params(axis='y', which='both', right=True, labelright=False, left=True, labelleft=True)

        self.ax.set_xlim(self.start_date, self.start_date + timedelta(days=1))
        if self.filtred_values:
            self.ax.set_ylim(min(self.filtred_values), max(self.filtred_values))
        else:
            self.show_message(
                self.util.dict_language[self.lang]["mgbox_error"],
                self.util.dict_language[self.lang]["mgbox_error_noinfo_period"]
            )
            self.can_plot = False
            return

        self.ax.set_ylabel(F'{", ".join(plot_type)} ({self.get_measure(plot_type)})')
        self.ax.set_xlabel('UT')
        self.ax.set_title(f'{station} {self.start_date.day:02}/{self.start_date.month:02}/{self.start_date.year} - {final_date.day:02}/{final_date.month:02}/{final_date.year}')

        if self.bold_text:
            self.ax.xaxis.label.set_weight('bold')
            self.ax.yaxis.label.set_weight('bold')
            self.ax.title.set_weight('bold')
            for label in self.ax.get_xticklabels() + self.ax.get_yticklabels():
                label.set_fontweight('bold')
        
        if self.grid_graph:
            self.ax.grid()
        
        self.fig.canvas.mpl_connect('button_press_event', lambda event: self.create_exporter_level_top(event, plot_type))

    # PyQt5 message box
    def show_message(self, title, message):
        QMessageBox.information(self.root, title, message)
