from Model.GraphPage.GraphsModule import GraphsModule
from Model.Custom.CustomPltOptions import CustomPltOptions
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from PyQt5.QtWidgets import QMessageBox

class ManyGraphs(GraphsModule):
    def __init__(self, root, language):
        self.root = root
        self.lang = language
        super().__init__(self.lang, self.root)

    # creates one graph that has all data in a period of time
    def plot_more_days(self, local_downloaded, stations, selected_types, bold_text, grid_graph, start, end, selected_dates, cal_selection, data_with_stations, number_columns=0, number_rows=0):
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
        if not self.validate_grid(number_columns, number_rows): 
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

        self.add_plots(selected_types, number_rows, number_columns)
        if not self.can_plot:
            return
        
        self.fig.canvas.manager.toolmanager.add_tool(
            'Graph Info', 
            CustomPltOptions, 
            inform_graph=lambda: self.inform_graph(selected_types, avarage_types)
        )
        self.fig.canvas.manager.toolbar.add_tool('Graph Info', 'io')
        plt.show()

    # Check if grid (columns x rows) matches the number of days in the range
    def validate_grid(self, number_columns, number_rows):
        difference_dates = self.end_date - self.start_date
        if number_columns * number_rows != difference_dates.days:
            self.show_message(
                self.util.dict_language[self.lang]["mgbox_error"],
                self.util.dict_language[self.lang]["mgbox_error_rowcol"]
            )
            return False
        return True

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

    # plot and config the given data
    def add_plots(self, slct_types, number_rows, number_columns):
        try:
            final_date = self.end_date - timedelta(days=1)
            plt.close('all')
            plt.rcParams['toolbar'] = 'toolmanager' # allows custom tools mode
            self.fig, axs = plt.subplots(number_rows, number_columns)
            self.axs = axs.flatten()
            self.filtred_values = []  
            self.current_date = self.start_date

            for plot_type in slct_types:
                control_reference = True
                for station in self.stations:
                    for dy, (day, times) in enumerate(self.all_data[station].items()):
                        plot_values = []
                        for time in times:
                            data = self.all_data[station][day][time][plot_type]
                            if data is not None: self.filtred_values.append(data)
                            plot_values.append(data)

                        time_axis = [self.start_date + timedelta(minutes=min) for min in range(1440)]
                        if 'reference' in plot_type:
                            if control_reference:  # evita repetir a referência
                                self.axs[dy].plot(time_axis, plot_values, label=plot_type)
                        else:
                            self.axs[dy].plot(time_axis, plot_values, label=f'{station}-{plot_type}')

                        timehour = [self.current_date + timedelta(hours=h) for h in range(24)]
                        self.axs[dy].minorticks_on()
                        self.axs[dy].set_xticks(timehour, minor=True)
                        self.axs[dy].xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
                        self.axs[dy].tick_params(axis='x', which='both', top=True, labeltop=False, bottom=True, labelbottom=True)
                        self.axs[dy].tick_params(axis='y', which='both', right=True, labelright=False, left=True, labelleft=True)

                        self.axs[dy].set_xlim(self.start_date, self.start_date + timedelta(hours=24))
                        if self.filtred_values:
                            self.axs[dy].set_ylim(min(self.filtred_values), max(self.filtred_values))
                        else:
                            self.show_message(
                                self.util.dict_language[self.lang]["mgbox_error"],
                                self.util.dict_language[self.lang]["mgbox_error_noinfo_period"]
                            )
                            self.can_plot = False
                            return

                        self.axs[dy].set_ylabel(f'{plot_type} ({self.get_measure(plot_type)})')
                        self.axs[dy].set_xlabel('UT')
                        self.axs[dy].set_title(f'{self.current_date.day:02}/{self.current_date.month:02}/{self.current_date.year}')
                        self.current_date += timedelta(days=1)
                        self.axs[dy].legend()

                        if self.bold_text:
                            self.axs[dy].xaxis.label.set_weight('bold')
                            self.axs[dy].yaxis.label.set_weight('bold')
                            self.axs[dy].title.set_weight('bold')
                            for label in self.axs[dy].get_xticklabels() + self.axs[dy].get_yticklabels():
                                label.set_fontweight('bold')

                        if self.grid_graph:
                            self.axs[dy].grid()

                    self.fig.suptitle(f'{plot_type} {self.start_date.strftime("%d/%m/%Y")} - {final_date.strftime("%d/%m/%Y")}')
                    plt.tight_layout()
                    plt.subplots_adjust(wspace=0.4, hspace=0.4)
                    control_reference = False
                    
            self.fig.canvas.mpl_connect('button_press_event', lambda event: self.create_exporter_level_top(event, slct_types))

        except Exception as error:
            self.show_message(
                self.util.dict_language[self.lang]["mgbox_error"],
                self.util.dict_language[self.lang]["mgbox_error_plt"]
            )
            self.can_plot = False
            print(error)
