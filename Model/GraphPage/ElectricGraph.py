from Model.GraphPage.GraphsModule import GraphsModule
from Model.GraphPage.GeoIndexHandler import GeoIndexHandler
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import math
import matplotlib.dates as mdates
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QDate
import math
import re
import os

class ElectricGraph(GraphsModule):
    def __init__(self, root, language):
        self.geo_index_handler = GeoIndexHandler()
        self.root = root
        self.lang = language
        super().__init__(self.lang)

    def plot_electric_field(self, bold_text, grid_graph, start, end, files, field):
        # se não tiver 'd' no em qualquer um dos tipos, retorne
        self.bold_text = bold_text
        self.grid_graph = grid_graph
        self.start = start
        self.end = end
        self.field = field

        self.sorted_files = []
        self.stations = []
        self.filtred_values = []
        self.can_plot = False

        if files:
            files_dict = {}
            dates = []
            for file in files:
                filename = os.path.basename(file)
                match = re.search(r'(\d{8})', filename)
                if match:
                    station = filename[:match.start()]
                    if station not in files_dict: 
                        files_dict[station] = []
                    files_dict[station].append(file)
                    try:
                        dates.append(datetime.strptime(match.group(1), '%Y%m%d').date())
                    except ValueError: pass
            self.sorted_files = list(files_dict.values())
            self.stations = list(files_dict.keys())
            
            if dates:
                self.start_date = min(dates)
                self.end_date = max(dates) + timedelta(days=1)
            else:
                self.start_date, self.end_date = self.format_dates(start, end)
                if not self.start_date: return
                self.end_date += timedelta(days=1)
        else:
            self.start_date, self.end_date = self.format_dates(start, end)
            if not self.start_date: 
                return
            self.end_date += timedelta(days=1)
            self.all_data = self.get_stations_data()
            if not self.all_data:
                return
            self.stations = list(self.all_data.keys())
        
        self.can_plot = True
        self.info_time = None
        
        self.add_plots()
        if self.field:
            type = ["mV/m"]
        else:
            type = ["m/s"]
        self.config_graph(type, ', '.join(self.stations))
        if not self.can_plot:
            return
        
        plt.show()

        year_config = self.util.get_year_config()
        final_config = self.util.get_final_config()

        if self.start_date.day != year_config[0] or self.start_date.month != year_config[1] or self.start_date.year != year_config[2]:
            print("ElectricGraph - plot_electric_field")
            print("Start Date:", self.start_date)
            print("Year Config:", year_config)
            self.util.change_year([self.start_date.day, self.start_date.month, self.start_date.year])
        if self.end_date.day - 1 != final_config[0] or self.end_date.month != final_config[1] or self.end_date.year != final_config[2]:
            print("ElectricGraph - plot_electric_field")
            print("End Date:", self.end_date)
            print("Final Config:", final_config)
            self.util.change_final([self.end_date.day - 1, self.end_date.month, self.end_date.year])
    

    def add_plots(self):
        try:
            plt.close('all')
            self.fig, self.ax = plt.subplots()

            if isinstance(self.start_date, QDate):
                self.start_date = self.start_date.toPyDate()
            if isinstance(self.end_date, QDate):
                self.end_date = self.end_date.toPyDate()
            
            # First, gather all data and plot it
            if self.sorted_files:
                for file_list in self.sorted_files:
                    if not file_list: continue
                    
                    first_filename = os.path.basename(file_list[0])
                    match = re.search(r'(\d{8})', first_filename)
                    station = first_filename[:match.start()] if match else "Unknown"
                    
                    x_vals = []
                    y_vals = []
                    
                    for file_path in file_list:
                        filename = os.path.basename(file_path)
                        match = re.search(r'(\d{8})', filename)
                        if not match: continue
                        
                        date_str = match.group(1)
                        try:
                            current_date = datetime.strptime(date_str, '%Y%m%d').date()
                        except ValueError: continue
                        
                        try:
                            with open(file_path, 'r') as f:
                                lines = f.readlines()
                        except: continue
                        
                        for line in lines:
                            parts = line.split()
                            if len(parts) < 2: continue
                            
                            time_str = parts[0]
                            try:
                                val = float(parts[1])
                            except ValueError: continue
                            
                            try:
                                t = datetime.strptime(time_str, '%H:%M').time()
                            except ValueError: continue
                            
                            dt = datetime.combine(current_date, t)
                            
                            lt_dt = self.lt_transformer(dt)
                            lt_hour = lt_dt.hour + lt_dt.minute / 60.0
                            doy = self.doy_transformer(dt)
                            year = dt.year
                            
                            indices = self.geo_index_handler.get_indices(dt)
                            if indices:
                                if math.isnan(indices['f107']) or math.isnan(indices['f107a']):
                                    continue
                                
                                vd = self.vertical_drift(val, lt_hour, year, indices['f107'], indices['f107a'], indices['ap'], indices['kp'], doy)
                                x_vals.append(dt)
                                if self.field:
                                    ef = vd / 40.0
                                    y_vals.append(ef)
                                    self.filtred_values.append(ef)
                                else:
                                    y_vals.append(vd)
                                    self.filtred_values.append(vd)
                    
                    if x_vals and y_vals:
                        sorted_data = sorted(zip(x_vals, y_vals))
                        x_sorted, y_sorted = zip(*sorted_data)
                        self.ax.plot(x_sorted, y_sorted, label=f'{station}')

        except Exception as e:
            QMessageBox.information(
                None,
                "erro",
                str(e)
                ) 

    def config_graph(self, plot_type, station):
        if isinstance(self.start_date, QDate):
            self.start_date = self.start_date.toPyDate()
        if isinstance(self.end_date, QDate):
            self.end_date = self.end_date.toPyDate
        
        final_date = self.end_date - timedelta(days=1)
        timeday = [self.start_date + timedelta(days=i) for i in range((self.end_date - self.start_date).days+1)]
        self.ax.set_xticks(timeday, minor= False)
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter(f'%d'))

        self.ax.tick_params(axis='x', which='both', top=True, labeltop=False, bottom=True, labelbottom=True)
        self.ax.tick_params(axis='y', which='both', right=True, labelright=False, left=True, labelleft=True)

        self.ax.set_xlim(self.start_date, self.end_date)
        try:
            self.ax.set_ylim(min(self.filtred_values), max(self.filtred_values))
        except ValueError:
            QMessageBox.information(
                None,
                self.util.dict_language[self.lang]["mgbox_error"],
                self.util.dict_language[self.lang]["mgbox_error_noinfo_period"]
            )
            self.can_plot = False
            plt.close(self.fig)  # Fecha a figura para não exibir um gráfico vazio
            return 
        
        if self.field:
            self.ax.set_ylabel('Electric Field (mV/m)')
        else:
            self.ax.set_ylabel('Vertical Drift (m/s)')
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

        self.fig.canvas.mpl_connect('button_press_event', lambda event: self.create_exporter_level_top(event, plot_type, is_field=self.field))

    def lt_transformer(self, date_time):
        utc_offset = -3  # UTC-3
        return date_time + timedelta(hours=utc_offset)
    
    def doy_transformer(self, date_time):
        return date_time.timetuple().tm_yday
    
    def vertical_drift(self, dH, lt_hour, year, f107, f107a, ap_daily, kp, doy):
        vd = float(
            -1989.51 + 1.002 * year - 0.00022 * doy - 0.0222 * f107 #f107 no lugar do 71.1
            -0.0282 * f107a - 0.0229 * ap_daily + 0.0589 * kp - 0.3661 * lt_hour #kp no lugar do 5 ||| Ap no lugar do 67
            + 0.1865 * dH + 0.00028 * dH**2 - 0.0000023 * dH**3
        )
        return vd
