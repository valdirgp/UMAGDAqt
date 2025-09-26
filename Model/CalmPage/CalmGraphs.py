from Model.GraphPage.GraphsModule import GraphsModule
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from PyQt5.QtWidgets import QMessageBox
import os
import math

class CalmModel(GraphsModule):
    def __init__(self, root, language):
        self.root = root
        self.lang = language

        self.start_date = None
        self.end_date = None
        self.station = None
        self.data_with_stations = None
        self.temp_window = None

        super().__init__(self.lang)

    # Creates one graph that has all data in a period of time
    def create_graphics_calm(self, local_downloaded, start, end, station, data_with_stations, get_selected_calm_dates, type):
        self.lcl_downloaded = local_downloaded
        self.station = station.split()[0]
        self.data_with_stations = data_with_stations
        self.selected_calm_dates = get_selected_calm_dates
        
        if self.station is None or self.data_with_stations.get(self.station) is None:
            QMessageBox.information(
                None,
                self.util.dict_language[self.lang]["mgbox_error"],
                self.util.dict_language[self.lang]["mgbox_error_st"]
            )
            return
        
        # Validate dates
        self.start_date, self.end_date = self.format_dates(start, end)
        if not self.start_date: return

        # Gather data from the station
        self.data_all = self.gather_station_data()
        if not self.data_all:
            return

        # Plot data
        if type == "H":
            self.plot_calm_avg_H()
        elif type == "Z":
            self.plot_calm_avg_Z()
        

    # Collects data for the selected station within the date range
    def gather_station_data(self):
        station_data = []
        current_date = self.start_date

        while current_date <= self.end_date:
            single_data = self.get_data(current_date, self.station, self.data_with_stations[f'{self.station}'][0])
            station_data.append(single_data)
            current_date += timedelta(days=1)
        return station_data

    '''
    # Plot the given data using H(nT)
    def plot_calm_avg_H(self):
        plt.close("all")
        fig, ax = plt.subplots(figsize=(10, 6))
        calm_averages_H = self.calculate_calm_average_H()
        calm_avgPstd_H = self.calculate_calm_averagePstd_H()
        calm_avgMstd_H = self.calculate_calm_averageMstd_H()

        time = [self.start_date + timedelta(minutes=i) for i in range(len(calm_averages_H))]

        ax.plot(time, calm_averages_H, label='Calm Days', color='black', linewidth=2)
        ax.plot(time, calm_avgPstd_H, label='Calm Days avg + std dev', color='gray', linewidth=1)
        ax.plot(time, calm_avgMstd_H, label='Calm Days avg - std dev', color='gray', linewidth=1)

        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        ax.set_ylabel('H(nT)')
        ax.set_xlabel('Time')
        ax.set_title(f"Station: {self.station}")
        ax.grid(True)
        ax.legend()
        ax.set_xlim(left=time[0], right=time[-1])

        fig.suptitle('Calm Days H(nT) Data')
        plt.subplots_adjust(left=0.1)
        plt.show()
    '''

    def plot_calm_avg_H(self):
        plt.close("all")
        fig, ax = plt.subplots(figsize=(10, 6))

        calm_averages_H = self.calculate_calm_average_H()
        calm_avgPstd_H = self.calculate_calm_averagePstd_H()
        calm_avgMstd_H = self.calculate_calm_averageMstd_H()

        # Garantir que o eixo X seja datetime contínuo
        disturbed_day = self.selected_calm_dates[0]  # ou use qualquer dia de referência
        base_time = datetime.combine(disturbed_day, datetime.min.time())
        time = [base_time + timedelta(minutes=i) for i in range(len(calm_averages_H))]

        ax.plot(time, calm_averages_H, label='Calm Days', color='black', linewidth=2)
        ax.plot(time, calm_avgPstd_H, label='Calm Days avg + std dev', color='gray', linewidth=1)
        ax.plot(time, calm_avgMstd_H, label='Calm Days avg - std dev', color='gray', linewidth=1)

        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=2))
        ax.xaxis.set_minor_locator(mdates.MinuteLocator(interval=30))
        fig.autofmt_xdate()

        ax.set_ylabel('H(nT)')
        ax.set_xlabel('Time')
        ax.set_title(f"Station: {self.station}")
        ax.grid(True)
        ax.legend()
        ax.set_xlim(time[0], time[-1])

        fig.suptitle('Calm Days H(nT) Data')
        plt.subplots_adjust(left=0.1)
        plt.show()

    '''    
    # Plot the given data using Z(nT)
    def plot_calm_avg_Z(self):
        plt.close("all")
        fig, ax = plt.subplots(figsize=(10, 6))
        calm_averages_Z = self.calculate_calm_average_Z()
        calm_avgPstd_Z = self.calculate_calm_averagePstd_Z()
        calm_avgMstd_Z = self.calculate_calm_averageMstd_Z()

        time = [self.start_date + timedelta(minutes=i) for i in range(len(calm_averages_Z))]

        ax.plot(time, calm_averages_Z, label='Calm Days', color='black', linewidth=2)
        ax.plot(time, calm_avgPstd_Z, label='Calm Days avg + std dev', color='gray', linewidth=1)
        ax.plot(time, calm_avgMstd_Z, label='Calm Days avg - std dev', color='gray', linewidth=1)

        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        ax.set_ylabel('Z(nT)')
        ax.set_xlabel('Time')
        ax.set_title(f"Station: {self.station}")
        ax.grid(True)
        ax.legend()
        ax.set_xlim(left=time[0], right=time[-1])

        fig.suptitle('Calm Days Z(nT) Data')
        plt.subplots_adjust(left=0.1)
        plt.show()
    '''

    def plot_calm_avg_Z(self):
        plt.close("all")
        fig, ax = plt.subplots(figsize=(10, 6))

        calm_averages_Z = self.calculate_calm_average_Z()
        calm_avgPstd_Z = self.calculate_calm_averagePstd_Z()
        calm_avgMstd_Z = self.calculate_calm_averageMstd_Z()

        # Garantir que o eixo X seja datetime contínuo
        disturbed_day = self.selected_calm_dates[0]  # ou use qualquer dia de referência
        base_time = datetime.combine(disturbed_day, datetime.min.time())
        time = [base_time + timedelta(minutes=i) for i in range(len(calm_averages_Z))]

        ax.plot(time, calm_averages_Z, label='Calm Days', color='black', linewidth=2)
        ax.plot(time, calm_avgPstd_Z, label='Calm Days avg + std dev', color='gray', linewidth=1)
        ax.plot(time, calm_avgMstd_Z, label='Calm Days avg - std dev', color='gray', linewidth=1)

        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=2))
        ax.xaxis.set_minor_locator(mdates.MinuteLocator(interval=30))
        fig.autofmt_xdate()

        ax.set_ylabel('Z(nT)')
        ax.set_xlabel('Time')
        ax.set_title(f"Station: {self.station}")
        ax.grid(True)
        ax.legend()
        ax.set_xlim(time[0], time[-1])

        fig.suptitle('Calm Days Z(nT) Data')
        plt.subplots_adjust(left=0.1)
        plt.show()

        
    # Pega a data inicial e final, lista dos nomes das estações e os dados das estações
    def get_cal_datas(self, selected_dates): 
        data = []
        for date in selected_dates:
            data.append(self.get_data(date, self.station, self.data_with_stations[f'{self.station}'][0]))
        return data

    # Calculates the average for calm days using selected_calm_dates.
    def calculate_calm_average_H(self):
        calm_averages_H = []
        calm_values = self.get_cal_datas(self.selected_calm_dates) 
        for hour in range(1440):
            try:
                H_data = []
                for i, _ in enumerate(calm_values):            
                    H_data.append(calm_values[i][hour]['H'])
                average = sum(H_data) / len(self.selected_calm_dates)
                calm_averages_H.append(average)
            except Exception:
                calm_averages_H.append(None)
        return calm_averages_H
    
    # Average + Std Dev
    def calculate_calm_averagePstd_H(self):
        calm_avgPstd_H = []
        calm_values = self.get_cal_datas(self.selected_calm_dates) 
        for hour in range(1440):
            try:
                H_data = []
                for i, _ in enumerate(calm_values):            
                    H_data.append(calm_values[i][hour]['H'])
                average = sum(H_data) / len(self.selected_calm_dates)
                variance = sum((x - average) ** 2 for x in H_data) / len(H_data)
                std = variance ** 0.5 + average
                calm_avgPstd_H.append(std)
            except Exception:
                calm_avgPstd_H.append(None)
        return calm_avgPstd_H
    
    # Average - Std Dev
    def calculate_calm_averageMstd_H(self):
        calm_avgMstd_H = []
        calm_values = self.get_cal_datas(self.selected_calm_dates) 
        for hour in range(1440):
            try:
                H_data = []
                for i, _ in enumerate(calm_values):            
                    H_data.append(calm_values[i][hour]['H'])
                average = sum(H_data) / len(self.selected_calm_dates)
                variance = sum((x - average) ** 2 for x in H_data) / len(H_data)
                std = average - variance ** 0.5
                calm_avgMstd_H.append(std)
            except Exception:
                calm_avgMstd_H.append(None)
        return calm_avgMstd_H

    # Calculates the average (Using Z(nT)) for calm days using selected_calm_dates.
    def calculate_calm_average_Z(self):
        calm_averages_Z = []
        calm_values = self.get_cal_datas(self.selected_calm_dates) 
        for hour in range(1440):
            try:
                Z_data = []
                for i, _ in enumerate(calm_values):            
                    Z_data.append(calm_values[i][hour]['Z'])
                average = sum(Z_data) / len(self.selected_calm_dates)
                calm_averages_Z.append(average)
            except Exception:
                calm_averages_Z.append(None)
        return calm_averages_Z
    
    # Average + Std Dev
    def calculate_calm_averagePstd_Z(self):
        calm_avgPstd_Z = []
        calm_values = self.get_cal_datas(self.selected_calm_dates) 
        for hour in range(1440):
            try:
                Z_data = []
                for i, _ in enumerate(calm_values):            
                    Z_data.append(calm_values[i][hour]['Z'])
                average = sum(Z_data) / len(self.selected_calm_dates)
                variance = sum((x - average) ** 2 for x in Z_data) / len(Z_data)
                std = variance ** 0.5 + average
                calm_avgPstd_Z.append(std)
            except Exception:
                calm_avgPstd_Z.append(None)
        return calm_avgPstd_Z
    
    # Average - Std Dev
    def calculate_calm_averageMstd_Z(self):
        calm_avgMstd_Z = []
        calm_values = self.get_cal_datas(self.selected_calm_dates) 
        for hour in range(1440):
            try:
                Z_data = []
                for i, _ in enumerate(calm_values):            
                    Z_data.append(calm_values[i][hour]['Z'])
                average = sum(Z_data) / len(self.selected_calm_dates)
                variance = sum((x - average) ** 2 for x in Z_data) / len(Z_data)
                std = average - variance ** 0.5
                calm_avgMstd_Z.append(std)
            except Exception:
                calm_avgMstd_Z.append(None)
        return calm_avgMstd_Z

    # Retrieves the data for a given station and date from the corresponding file
    def get_data(self, day, station, network_station):
        self.st = station
        self.day = day
        path_station = os.path.join(self.lcl_downloaded, 
                                    'Magnetometer', 
                                    network_station, 
                                    str(self.day.year), 
                                    self.st, 
                                    f'{self.st.lower()}{self.day.year}{self.day.month:02}{self.day.day:02}min.min'
                                    )
        is_header = True
        data = []

        try:
            with open(path_station, 'r') as file:
                lines = file.read().split('\n')
        except FileNotFoundError:
            return [{'D': None, 'H': None, 'Z': None, 'I': None, 'F': None, 'G': None, 'X': None, 'Y': None}] * 1440

        try:
            self.st = 'VSS' if (self.st == 'VSI') or (self.st == 'VSE') else self.st
            for line in lines:
                if line == '':
                    continue 
                if is_header:
                    if line.find('H(nT)') != -1:
                        is_header = False
                        archive_case = 'embrace:h'

                    if line.find(f'{self.st}X') != -1 and line.find(f'{self.st}F') != -1:
                        is_header = False
                        archive_case = 'intermagnet:x,y,f'

                    if line.find(f'{self.st}X') != -1 and line.find(f'{self.st}G') != -1:
                        is_header = False
                        archive_case = 'intermagnet:x,y,g'

                    if line.find(f'{self.st}H') != -1:
                        is_header = False
                        archive_case = 'intermagnet:h'

                else:
                    data_dict = {}
                    separated_data = line.split()
                    match archive_case:
                        case 'embrace:h':
                            try:
                                data_dict['D'] = float(separated_data[5]) if float(separated_data[5]) != 99999.00 else None
                                data_dict['H'] = float(separated_data[6]) if float(separated_data[6]) != 99999.00 else None
                                data_dict['Z'] = float(separated_data[7]) if float(separated_data[7]) != 99999.00 else None
                                data_dict['I'] = float(separated_data[8]) if float(separated_data[8]) != 99999.00 else None
                                data_dict['F'] = float(separated_data[9]) if float(separated_data[9]) != 99999.00 else None
                            except Exception as error:
                                print('error getting data: ', archive_case)

                        case 'intermagnet:x,y,f':
                            try:
                                if float(separated_data[3]) != 99999.00 and float(separated_data[4]) != 99999.00:   
                                    data_dict['H'] = math.sqrt(float(separated_data[3])**2+float(separated_data[4])**2)
                                else:
                                    data_dict['H'] = None
                                data_dict['X'] = float(separated_data[3]) if float(separated_data[3]) != 99999.00 else None
                                data_dict['Y'] = float(separated_data[4]) if float(separated_data[4]) != 99999.00 else None
                                data_dict['Z'] = float(separated_data[5]) if float(separated_data[5]) != 99999.00 else None
                                data_dict['F'] = float(separated_data[6]) if float(separated_data[6]) != 99999.00 else None
                            except Exception as error:
                                print('error getting data: ', archive_case)

                        case 'intermagnet:x,y,g':
                            try:
                                if float(separated_data[3]) != 99999.00 and float(separated_data[4]) != 99999.00:
                                    data_dict['H'] = math.sqrt(float(separated_data[3])**2+float(separated_data[4])**2)
                                else:
                                    data_dict['H'] = None
                                data_dict['X'] = float(separated_data[3]) if float(separated_data[3]) != 99999.00 else None
                                data_dict['Y'] = float(separated_data[4]) if float(separated_data[4]) != 99999.00 else None
                                data_dict['Z'] = float(separated_data[5]) if float(separated_data[5]) != 99999.00 else None
                                data_dict['G'] = float(separated_data[6]) if float(separated_data[6]) != 99999.00 else None
                            except Exception as error:
                                print('error getting data: ', archive_case)

                        case 'intermagnet:h':
                            try:
                                data_dict['H'] = float(separated_data[3]) if float(separated_data[3]) != 99999.00 else None
                                data_dict['D'] = float(separated_data[4]) if float(separated_data[4]) != 99999.00 else None
                                data_dict['Z'] = float(separated_data[5]) if float(separated_data[5]) != 99999.00 else None
                                data_dict['F'] = float(separated_data[6]) if float(separated_data[6]) != 99999.00 else None
                            except Exception as error:
                                print('error getting data: ', archive_case)

                    data.append(data_dict)
            return data
        except Exception as error:
            QMessageBox.information(
                None,
                self.util.dict_language[self.lang]["mgbox_error"],
                f'{self.util.dict_language[self.lang]["mgbox_error_info_ad"]}: {error}'
            )
            return data