from Model.GraphPage.GraphsModule import GraphsModule
from datetime import datetime, timedelta, time as dt_time
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
#import tkinter as tk
from PyQt5.QtWidgets import QMessageBox, QDateEdit, QCalendarWidget
from PyQt5.QtCore import QDate

import os
import math

#This code creates a graph that has the average and the average +/- Standard deviation of the h(nT) data of calm/quiet days and a separate line of a single disturbed day.
#Add plotting function for D, I, F, X, Y, Z

class UniversalCDModel(GraphsModule):
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
    def create_graphics_calm_distU_H(self, local_downloaded, start, end, station, data_with_stations, get_selected_calm_dates, selected_disturb_date):
        self.lcl_downloaded = local_downloaded
        self.station = station[0]
        # Garantir que data_with_stations seja um dicionário
        if not isinstance(data_with_stations, dict):
            raise TypeError(f"data_with_stations esperado como dict, mas recebeu {type(data_with_stations)}")
        self.data_with_stations = data_with_stations
        self.selected_calm_dates = get_selected_calm_dates
        self.selected_disturb_date = selected_disturb_date

        #print(f"type(station): {type(station)}, repr(station): {repr(station)}")

        if isinstance(start, QCalendarWidget):
            start = start.selectedDate().toPyDate()
        if isinstance(start, QDate):
            start = start.toPyDate()

        if isinstance(end, QCalendarWidget):
            end = end.selectedDate().toPyDate()
        if isinstance(end, QDate):
            end = end.toPyDate()


        # Validate dates
        self.start_date, self.end_date = self.format_dates(start, end)
        if not self.start_date: return

        # Gather data from the station
        self.data_all = self.gather_station_data()
        if not self.data_all:
            return

        # Plot H data
        self.plot_calm_avg_H()

    def create_graphics_calm_distU_Z(self, local_downloaded, start, end, station, data_with_stations, get_selected_calm_dates, selected_disturb_date):
        self.lcl_downloaded = local_downloaded
        self.station = station[0]
        self.data_with_stations = data_with_stations
        self.selected_calm_dates = get_selected_calm_dates
        self.selected_disturb_date = selected_disturb_date

        if isinstance(start, QCalendarWidget):
            start = start.selectedDate().toPyDate()
        if isinstance(start, QDate):
            start = start.toPyDate()

        if isinstance(end, QCalendarWidget):
            end = end.selectedDate().toPyDate()
        if isinstance(end, QDate):
            end = end.toPyDate()

        # Validate dates
        self.start_date, self.end_date = self.format_dates(start, end)
        if not self.start_date: return

        # Gather data from the station
        self.data_all = self.gather_station_data()
        if not self.data_all:
            return

        # Plot Z data
        self.plot_calm_avg_Z()

    def create_graphics_calm_distU_X(self, local_downloaded, start, end, station, data_with_stations, get_selected_calm_dates, selected_disturb_date):
        self.lcl_downloaded = local_downloaded
        self.station = station[0]
        self.data_with_stations = data_with_stations
        self.selected_calm_dates = get_selected_calm_dates
        self.selected_disturb_date = selected_disturb_date

        if isinstance(start, QCalendarWidget):
            start = start.selectedDate().toPyDate()
        if isinstance(start, QDate):
            start = start.toPyDate()

        if isinstance(end, QCalendarWidget):
            end = end.selectedDate().toPyDate()
        if isinstance(end, QDate):
            end = end.toPyDate()

        # Validate dates
        self.start_date, self.end_date = self.format_dates(start, end)
        if not self.start_date: return

        # Gather data from the station
        self.data_all = self.gather_station_data()
        if not self.data_all:
            return

        # Plot X data
        self.plot_calm_avg_X()
    
    def create_graphics_calm_distU_Y(self, local_downloaded, start, end, station, data_with_stations, get_selected_calm_dates, selected_disturb_date):
        self.lcl_downloaded = local_downloaded
        self.station = station[0]
        self.data_with_stations = data_with_stations
        self.selected_calm_dates = get_selected_calm_dates
        self.selected_disturb_date = selected_disturb_date

        if isinstance(start, QCalendarWidget):
            start = start.selectedDate().toPyDate()
        if isinstance(start, QDate):
            start = start.toPyDate()

        if isinstance(end, QCalendarWidget):
            end = end.selectedDate().toPyDate()
        if isinstance(end, QDate):
            end = end.toPyDate()

        # Validate dates
        self.start_date, self.end_date = self.format_dates(start, end)
        if not self.start_date: return

        # Gather data from the station
        self.data_all = self.gather_station_data()
        if not self.data_all:
            return

        # Plot Y data
        self.plot_calm_avg_Y()

    def create_graphics_calm_distU_D(self, local_downloaded, start, end, station, data_with_stations, get_selected_calm_dates, selected_disturb_date):
        self.lcl_downloaded = local_downloaded
        self.station = station[0]
        self.data_with_stations = data_with_stations
        self.selected_calm_dates = get_selected_calm_dates
        self.selected_disturb_date = selected_disturb_date

        if isinstance(start, QCalendarWidget):
            start = start.selectedDate().toPyDate()
        if isinstance(start, QDate):
            start = start.toPyDate()

        if isinstance(end, QCalendarWidget):
            end = end.selectedDate().toPyDate()
        if isinstance(end, QDate):
            end = end.toPyDate()

        # Validate dates
        self.start_date, self.end_date = self.format_dates(start, end)
        if not self.start_date: return

        # Gather data from the station
        self.data_all = self.gather_station_data()
        if not self.data_all:
            return

        # Plot D data
        self.plot_calm_avg_D()  

    def create_graphics_calm_distU_F(self, local_downloaded, start, end, station, data_with_stations, get_selected_calm_dates, selected_disturb_date):
        self.lcl_downloaded = local_downloaded
        self.station = station[0]
        self.data_with_stations = data_with_stations
        self.selected_calm_dates = get_selected_calm_dates
        self.selected_disturb_date = selected_disturb_date

        if isinstance(start, QCalendarWidget):
            start = start.selectedDate().toPyDate()
        if isinstance(start, QDate):
            start = start.toPyDate()

        if isinstance(end, QCalendarWidget):
            end = end.selectedDate().toPyDate()
        if isinstance(end, QDate):
            end = end.toPyDate()

        # Validate dates
        self.start_date, self.end_date = self.format_dates(start, end)
        if not self.start_date: return

        # Gather data from the station
        self.data_all = self.gather_station_data()
        if not self.data_all:
            return

        # Plot F data
        self.plot_calm_avg_F()  

    def create_graphics_calm_distU_I(self, local_downloaded, start, end, station, data_with_stations, get_selected_calm_dates, selected_disturb_date):
        self.lcl_downloaded = local_downloaded
        self.station = station[0]
        self.data_with_stations = data_with_stations
        self.selected_calm_dates = get_selected_calm_dates
        self.selected_disturb_date = selected_disturb_date

        if isinstance(start, QCalendarWidget):
            start = start.selectedDate().toPyDate()
        if isinstance(start, QDate):
            start = start.toPyDate()

        if isinstance(end, QCalendarWidget):
            end = end.selectedDate().toPyDate()
        if isinstance(end, QDate):
            end = end.toPyDate()

        # Validate dates
        self.start_date, self.end_date = self.format_dates(start, end)
        if not self.start_date: return

        # Gather data from the station
        self.data_all = self.gather_station_data()
        if not self.data_all:
            return

        # Plot I data
        self.plot_calm_avg_I()

    def create_graphics_calm_distU_G(self, local_downloaded, start, end, station, data_with_stations, get_selected_calm_dates, selected_disturb_date):
        self.lcl_downloaded = local_downloaded
        self.station = station[0]
        self.data_with_stations = data_with_stations
        self.selected_calm_dates = get_selected_calm_dates
        self.selected_disturb_date = selected_disturb_date

        if isinstance(start, QCalendarWidget):
            start = start.selectedDate().toPyDate()
        if isinstance(start, QDate):
            start = start.toPyDate()

        if isinstance(end, QCalendarWidget):
            end = end.selectedDate().toPyDate()
        if isinstance(end, QDate):
            end = end.toPyDate()

        # Validate dates
        self.start_date, self.end_date = self.format_dates(start, end)
        if not self.start_date: return

        # Gather data from the station
        self.data_all = self.gather_station_data()
        if not self.data_all:
            return

        # Plot G data
        self.plot_calm_avg_G()

    # Collects data for the selected station within the date range
    def gather_station_data(self):
        station_data = []
        current_date = self.start_date

        while current_date <= self.end_date:
            single_data = self.get_data(current_date, self.station, self.data_with_stations[f"{self.station}"][0])
            station_data.append(single_data)
            current_date += timedelta(days=1)
        return station_data
    
    def show_no_data_message(self, key):
            #tk.messagebox.showinfo(self.util.dict_language[self.lang]["lbl_err_plot"], self.util.dict_language[self.lang]["mgbox_err_plot"])
            QMessageBox.critical(
                None,
                self.util.dict_language[self.lang]["lbl_err_plot"],
                self.util.dict_language[self.lang]["mgbox_err_plot"] + f": {key}"
            )
    
    # Plot the given data
    def plot_calm_avg_H(self):
        # Plot the average of selected days with two lines for calm and disturbed days.
        try:
            plt.close("all")
            fig, ax = plt.subplots(figsize=(10, 6))
            calm_averages_H = self.calculate_calm_average_H()
            calm_avgPstd_H = self.calculate_calm_averagePstd_H()
            calm_avgMstd_H = self.calculate_calm_averageMstd_H()

            lista_legal = []
            disturbed_date_data = self.get_data(self.selected_disturb_date[0], self.station, self.data_with_stations[f'{self.station}'][0])

            for _, disturb in enumerate(disturbed_date_data):
                lista_legal.append(disturb['H'])

            #print(">>> DEBUG start_date:", self.start_date, type(self.start_date))
            #time = [self.start_date + timedelta(minutes=i) for i in range(len(calm_averages_H))]
            time = [datetime.combine(self.start_date, dt_time(hour=i//60, minute=i%60)) for i in range(1440)]

            ax.plot(time, calm_averages_H, label='Calm Days', color='black', linewidth = 2)
            ax.plot(time, calm_avgPstd_H, label='Calm Days avg + std dev', color='gray', linewidth = 1)
            ax.plot(time, calm_avgMstd_H, label='Calm Days avg - std dev', color='gray', linewidth = 1)
            ax.plot(time, lista_legal, label='Disturbed Day', color='red', linewidth = 1.5)
            #ax.fill_between(time, calm_avgMstd, calm_avgPstd, color='gray', alpha=0.2)

            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            ax.set_ylabel('H(nT)')
            ax.set_xlabel('Time')


            ax.set_title(f"Station: {self.station}, [{str(self.start_date)}] - [{str(self.end_date)}]")
            ax.grid(True)
            ax.legend()

            # Ajustar limites do eixo X para tocar o lado esquerdo
            ax.set_xlim(left=time[0], right=time[-1])

            fig.suptitle('Calm and Disturbed Days Data')
            plt.subplots_adjust(left=0.1)  # Ajuste do espaço entre o gráfico e a borda
            plt.show()

        except KeyError as key:
            self.show_no_data_message(key)
        except Exception as error:
            #tk.messagebox.showinfo("Error", f"Unexpected error while plotting: {error}")
            QMessageBox.critical(
                None,
                self.util.dict_language[self.lang]["mgbox_error"],
                (f"Unexpected error while plotting: {error}")
            )
            print(f"Unexpected error while plotting: {error}")

    def plot_calm_avg_Z(self):
        # Plot the average of selected days with two lines for calm and disturbed days.
        try:
            plt.close("all")
            fig, ax = plt.subplots(figsize=(10, 6))
            calm_averages_Z = self.calculate_calm_average_Z()
            calm_avgPstd_Z = self.calculate_calm_averagePstd_Z()
            calm_avgMstd_Z = self.calculate_calm_averageMstd_Z()

            lista_legal = []
            disturbed_date_data = self.get_data(self.selected_disturb_date[0], self.station, self.data_with_stations[f'{self.station}'][0])

            for _, disturb in enumerate(disturbed_date_data):
                lista_legal.append(disturb['Z'])

            #time = [self.start_date + timedelta(minutes=i) for i in range(len(calm_averages_Z))]
            time = [datetime.combine(self.start_date, dt_time(hour=i//60, minute=i%60)) for i in range(1440)]

            ax.plot(time, calm_averages_Z, label='Calm Days', color='black', linewidth = 2)
            ax.plot(time, calm_avgPstd_Z, label='Calm Days avg + std dev', color='gray', linewidth = 1)
            ax.plot(time, calm_avgMstd_Z, label='Calm Days avg - std dev', color='gray', linewidth = 1)
            ax.plot(time, lista_legal, label='Disturbed Day', color='red', linewidth = 1.5)
            #ax.fill_between(time, calm_avgMstd, calm_avgPstd, color='gray', alpha=0.2)

            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M')) #Hour:Month
            ax.set_ylabel('Z(nT)')
            ax.set_xlabel('Time')
            ax.set_title(f"Station: {self.station}, [{self.start_date}] - [{self.end_date}]")
            ax.grid(True)
            ax.legend()

            # Ajustar limites do eixo X para tocar o lado esquerdo
            ax.set_xlim(left=time[0], right=time[-1])

            fig.suptitle('Calm and Disturbed Days Data')
            plt.subplots_adjust(left=0.1)  # Ajuste do espaço entre o gráfico e a borda
            plt.show()

        except KeyError as key:
            self.show_no_data_message(key)
        except Exception as error:
            #tk.messagebox.showinfo("Error", f"Unexpected error while plotting: {error}")
            QMessageBox.critical(
                None,
                self.util.dict_language[self.lang]["mgbox_error"],
                (f"Unexpected error while plotting: {error}")
            )
            print(f"Unexpected error while plotting: {error}")

    def plot_calm_avg_X(self): # Put a pop up warning for when there's no available data
        # Plot the average of selected days with two lines for calm and disturbed days.
        try:
            plt.close("all")
            fig, ax = plt.subplots(figsize=(10, 6))
            calm_averages_X = self.calculate_calm_average_X()
            calm_avgPstd_X = self.calculate_calm_averagePstd_X()
            calm_avgMstd_X = self.calculate_calm_averageMstd_X()

            lista_legal = []
            disturbed_date_data = self.get_data(self.selected_disturb_date[0], self.station, self.data_with_stations[f'{self.station}'][0])

            for _, disturb in enumerate(disturbed_date_data):
                lista_legal.append(disturb['X'])

            #time = [self.start_date + timedelta(minutes=i) for i in range(len(calm_averages_X))]
            time = [datetime.combine(self.start_date, dt_time(hour=i//60, minute=i%60)) for i in range(1440)]

            ax.plot(time, calm_averages_X, label='Calm Days', color='black', linewidth = 2)
            ax.plot(time, calm_avgPstd_X, label='Calm Days avg + std dev', color='gray', linewidth = 1)
            ax.plot(time, calm_avgMstd_X, label='Calm Days avg - std dev', color='gray', linewidth = 1)
            ax.plot(time, lista_legal, label='Disturbed Day', color='red', linewidth = 1.5)
            #ax.fill_between(time, calm_avgMstd, calm_avgPstd, color='gray', alpha=0.2)

            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M')) #Hour:Month
            ax.set_ylabel('X(nT)')
            ax.set_xlabel('Time')
            ax.set_title(f"Station: {self.station}, [{self.start_date}] - [{self.end_date}]")
            ax.grid(True)
            ax.legend()

            # Ajustar limites do eixo X para tocar o lado esquerdo
            ax.set_xlim(left=time[0], right=time[-1])

            fig.suptitle('Calm and Disturbed Days Data')
            plt.subplots_adjust(left=0.1)  # Ajuste do espaço entre o gráfico e a borda
            plt.show()

        except KeyError as key: # If there's no available data for plotting, this message will appear.
            self.show_no_data_message(key)
        except Exception as error:
            #tk.messagebox.showinfo("Error", f"Unexpected error while plotting: {error}")
            QMessageBox.critical(
                None,
                self.util.dict_language[self.lang]["mgbox_error"],
                (f"Unexpected error while plotting: {error}")
            )
            print(f"Unexpected error while plotting: {error}")

    def plot_calm_avg_Y(self): # Put a pop up warning when there's no available data
        # Plot the average of selected days with two lines for calm and disturbed days.
        try:
            plt.close("all")
            fig, ax = plt.subplots(figsize=(10, 6))
            calm_averages_Y = self.calculate_calm_average_Y()
            calm_avgPstd_Y = self.calculate_calm_averagePstd_Y()
            calm_avgMstd_Y = self.calculate_calm_averageMstd_Y()

            lista_legal = []
            disturbed_date_data = self.get_data(self.selected_disturb_date[0], self.station, self.data_with_stations[f'{self.station}'][0])

            for _, disturb in enumerate(disturbed_date_data):
                lista_legal.append(disturb['Y'])

            #time = [self.start_date + timedelta(minutes=i) for i in range(len(calm_averages_Y))]
            time = [datetime.combine(self.start_date, dt_time(hour=i//60, minute=i%60)) for i in range(1440)]

            ax.plot(time, calm_averages_Y, label='Calm Days', color='black', linewidth = 2)
            ax.plot(time, calm_avgPstd_Y, label='Calm Days avg + std dev', color='gray', linewidth = 1)
            ax.plot(time, calm_avgMstd_Y, label='Calm Days avg - std dev', color='gray', linewidth = 1)
            ax.plot(time, lista_legal, label='Disturbed Day', color='red', linewidth = 1.5)
            #ax.fill_between(time, calm_avgMstd, calm_avgPstd, color='gray', alpha=0.2)

            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M')) #Hour:Month
            ax.set_ylabel('Y(nT)')
            ax.set_xlabel('Time')
            ax.set_title(f"Station: {self.station}, [{self.start_date}] - [{self.end_date}]")
            ax.grid(True)
            ax.legend()

            # Ajustar limites do eixo X para tocar o lado esquerdo
            ax.set_xlim(left=time[0], right=time[-1])

            fig.suptitle('Calm and Disturbed Days Data')
            plt.subplots_adjust(left=0.1)  # Ajuste do espaço entre o gráfico e a borda
            plt.show()

        except KeyError as key: # If there's no available data for plotting, this message will appear.
            self.show_no_data_message(key)
        except Exception as error:
            #tk.messagebox.showinfo("Error", f"Unexpected error while plotting: {error}")
            QMessageBox.critical(
                None,
                self.util.dict_language[self.lang]["mgbox_error"],
                (f"Unexpected error while plotting: {error}")
            )
            print(f"Unexpected error while plotting: {error}")

    def plot_calm_avg_D(self):
        # Plot the average of selected days with two lines for calm and disturbed days.
        try:
            plt.close("all")
            fig, ax = plt.subplots(figsize=(10, 6))
            calm_averages_D = self.calculate_calm_average_D()
            calm_avgPstd_D = self.calculate_calm_averagePstd_D()
            calm_avgMstd_D = self.calculate_calm_averageMstd_D()

            lista_legal = []
            disturbed_date_data = self.get_data(self.selected_disturb_date[0], self.station, self.data_with_stations[f'{self.station}'][0])

            for _, disturb in enumerate(disturbed_date_data):
                lista_legal.append(disturb['D'])

            #time = [self.start_date + timedelta(minutes=i) for i in range(len(calm_averages_D))]
            time = [datetime.combine(self.start_date, dt_time(hour=i//60, minute=i%60)) for i in range(1440)]

            ax.plot(time, calm_averages_D, label='Calm Days', color='black', linewidth = 2)
            ax.plot(time, calm_avgPstd_D, label='Calm Days avg + std dev', color='gray', linewidth = 1)
            ax.plot(time, calm_avgMstd_D, label='Calm Days avg - std dev', color='gray', linewidth = 1)
            ax.plot(time, lista_legal, label='Disturbed Day', color='red', linewidth = 1.5)
            #ax.fill_between(time, calm_avgMstd, calm_avgPstd, color='gray', alpha=0.2)

            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M')) #Hour:Month
            ax.set_ylabel('D(nT)')
            ax.set_xlabel('Time')
            ax.set_title(f"Station: {self.station}, [{self.start_date}] - [{self.end_date}]")
            ax.grid(True)
            ax.legend()

            # Ajustar limites do eixo X para tocar o lado esquerdo
            ax.set_xlim(left=time[0], right=time[-1])

            fig.suptitle('Calm and Disturbed Days Data')
            plt.subplots_adjust(left=0.1)  # Ajuste do espaço entre o gráfico e a borda
            plt.show()
        
        except KeyError as key: # If there's no available data for plotting, this message will appear.
            self.show_no_data_message(key)
        except Exception as error:
            #tk.messagebox.showinfo("Error", f"Unexpected error while plotting: {error}")
            QMessageBox.critical(
                None,
                self.util.dict_language[self.lang]["mgbox_error"],
                (f"Unexpected error while plotting: {error}")
            )
            print(f"Unexpected error while plotting: {error}")
    
    def plot_calm_avg_F(self):
        # Plot the average of selected days with two lines for calm and disturbed days.
        try:
            plt.close("all")
            fig, ax = plt.subplots(figsize=(10, 6))
            calm_averages_F = self.calculate_calm_average_F()
            calm_avgPstd_F = self.calculate_calm_averagePstd_F()
            calm_avgMstd_F = self.calculate_calm_averageMstd_F()

            lista_legal = []
            disturbed_date_data = self.get_data(self.selected_disturb_date[0], self.station, self.data_with_stations[f'{self.station}'][0])

            for _, disturb in enumerate(disturbed_date_data):
                lista_legal.append(disturb['F'])

            #time = [self.start_date + timedelta(minutes=i) for i in range(len(calm_averages_F))]
            time = [datetime.combine(self.start_date, dt_time(hour=i//60, minute=i%60)) for i in range(1440)]

            ax.plot(time, calm_averages_F, label='Calm Days', color='black', linewidth = 2)
            ax.plot(time, calm_avgPstd_F, label='Calm Days avg + std dev', color='gray', linewidth = 1)
            ax.plot(time, calm_avgMstd_F, label='Calm Days avg - std dev', color='gray', linewidth = 1)
            ax.plot(time, lista_legal, label='Disturbed Day', color='red', linewidth = 1.5)
            #ax.fill_between(time, calm_avgMstd, calm_avgPstd, color='gray', alpha=0.2)

            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M')) #Hour:Month
            ax.set_ylabel('F(nT)')
            ax.set_xlabel('Time')
            ax.set_title(f"Station: {self.station}, [{self.start_date}] - [{self.end_date}]")
            ax.grid(True)
            ax.legend()

            # Ajustar limites do eixo X para tocar o lado esquerdo
            ax.set_xlim(left=time[0], right=time[-1])

            fig.suptitle('Calm and Disturbed Days Data')
            plt.subplots_adjust(left=0.1)  # Ajuste do espaço entre o gráfico e a borda
            plt.show()

        except KeyError as key: # If there's no available data for plotting, this message will appear.
            self.show_no_data_message(key)
        except Exception as error:
            #tk.messagebox.showinfo("Error", f"Unexpected error while plotting: {error}")
            QMessageBox.critical(
                None,
                self.util.dict_language[self.lang]["mgbox_error"],
                (f"Unexpected error while plotting: {error}")
            )
            print(f"Unexpected error while plotting: {error}")

    def plot_calm_avg_I(self):
        # Plot the average of selected days with two lines for calm and disturbed days.
        try:
            plt.close("all")
            fig, ax = plt.subplots(figsize=(10, 6))
            calm_averages_I = self.calculate_calm_average_I()
            calm_avgPstd_I = self.calculate_calm_averagePstd_I()
            calm_avgMstd_I = self.calculate_calm_averageMstd_I()

            lista_legal = []
            disturbed_date_data = self.get_data(self.selected_disturb_date[0], self.station, self.data_with_stations[f'{self.station}'][0])

            for _, disturb in enumerate(disturbed_date_data):
                lista_legal.append(disturb['I'])

            #time = [self.start_date + timedelta(minutes=i) for i in range(len(calm_averages_I))]
            time = [datetime.combine(self.start_date, dt_time(hour=i//60, minute=i%60)) for i in range(1440)]

            ax.plot(time, calm_averages_I, label='Calm Days', color='black', linewidth = 2)
            ax.plot(time, calm_avgPstd_I, label='Calm Days avg + std dev', color='gray', linewidth = 1)
            ax.plot(time, calm_avgMstd_I, label='Calm Days avg - std dev', color='gray', linewidth = 1)
            ax.plot(time, lista_legal, label='Disturbed Day', color='red', linewidth = 1.5)
            #ax.fill_between(time, calm_avgMstd, calm_avgPstd, color='gray', alpha=0.2)

            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M')) #Hour:Month
            ax.set_ylabel('I(nT)')
            ax.set_xlabel('Time')
            ax.set_title(f"Station: {self.station}, [{self.start_date}] - [{self.end_date}]")
            ax.grid(True)
            ax.legend()

            # Ajustar limites do eixo X para tocar o lado esquerdo
            ax.set_xlim(left=time[0], right=time[-1])

            fig.suptitle('Calm and Disturbed Days Data')
            plt.subplots_adjust(left=0.1)  # Ajuste do espaço entre o gráfico e a borda
            plt.show()    

        except KeyError as key: # If there's no available data for plotting, this message will appear.
            self.show_no_data_message(key)
        except Exception as error:
            #tk.messagebox.showinfo("Error", f"Unexpected error while plotting: {error}")
            QMessageBox.critical(
                None,
                self.util.dict_language[self.lang]["mgbox_error"],
                (f"Unexpected error while plotting: {error}")
            )
            print(f"Unexpected error while plotting: {error}")

    def plot_calm_avg_G(self): # Put a pop up for when there's no available data
        # Plot the average of selected days with two lines for calm and disturbed days.
        try:
            plt.close("all")
            fig, ax = plt.subplots(figsize=(10, 6))
            calm_averages_G = self.calculate_calm_average_G()
            calm_avgPstd_G = self.calculate_calm_averagePstd_G()
            calm_avgMstd_G = self.calculate_calm_averageMstd_G()

            lista_legal = []
            disturbed_date_data = self.get_data(self.selected_disturb_date[0], self.station, self.data_with_stations[f'{self.station}'][0])

            for _, disturb in enumerate(disturbed_date_data):
                lista_legal.append(disturb['G'])

            #time = [self.start_date + timedelta(minutes=i) for i in range(len(calm_averages_G))]
            time = [datetime.combine(self.start_date, dt_time(hour=i//60, minute=i%60)) for i in range(1440)]

            ax.plot(time, calm_averages_G, label='Calm Days', color='black', linewidth = 2)
            ax.plot(time, calm_avgPstd_G, label='Calm Days avg + std dev', color='gray', linewidth = 1)
            ax.plot(time, calm_avgMstd_G, label='Calm Days avg - std dev', color='gray', linewidth = 1)
            ax.plot(time, lista_legal, label='Disturbed Day', color='red', linewidth = 1.5)
            #ax.fill_between(time, calm_avgMstd, calm_avgPstd, color='gray', alpha=0.2)

            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M')) #Hour:Month
            ax.set_ylabel('G(nT)')
            ax.set_xlabel('Time')
            ax.set_title(f"Station: {self.station}, [{self.start_date}] - [{self.end_date}]")
            ax.grid(True)
            ax.legend()

            # Ajustar limites do eixo X para tocar o lado esquerdo
            ax.set_xlim(left=time[0], right=time[-1])

            fig.suptitle('Calm and Disturbed Days Data')
            plt.subplots_adjust(left=0.1)  # Ajuste do espaço entre o gráfico e a borda
            plt.show()   
        
        except KeyError as key: #If there's no available data for plotting, this message will appear.
            self.show_no_data_message(key)
        except Exception as error: #If an error occurs, this message will appear alonside the type of error.
            #tk.messagebox.showinfo("Error", f"Unexpected error while plotting: {error}")
            QMessageBox.critical(
                None,
                self.util.dict_language[self.lang]["mgbox_error"],
                (f"Unexpected error while plotting: {error}")
            )
            print(f"Unexpected error while plotting: {error}")
    
    def get_cal_datas(self, selected_dates): #Pega a data inicial e final, lista dos nomes das estações e os dados das estações
        data = []
        for date in selected_dates:
            data.append(self.get_data(date, self.station, self.data_with_stations[f'{self.station}'][0]))
        return data

    def calculate_calm_average_H(self):
        # Calculate the average for calm days using selected_calm_dates./Calcular a média para os dias calmos usando selected_calm_dates.
        calm_averages_H = []
        calm_values = self.get_cal_datas(self.selected_calm_dates) 
        for hour in range(1440):
            try:
                H_data = []
                for i,_ in enumerate(calm_values):            
                    #calm_values[i][hour]['H'], onde i é os dias selecionados, hour é cada minuto do dia e 'H' é os valores de H das estações
                    H_data.append(calm_values[i][hour]['H'])
                average = sum(H_data)/len(self.selected_calm_dates)
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
                    for i,_ in enumerate(calm_values):            
                        #calm_values[i][hour]['H'], onde i é os dias selecionados, hour é cada minuto do dia e 'H' é os valores de H das estações
                        H_data.append(calm_values[i][hour]['H'])
                    average = sum(H_data)/len(self.selected_calm_dates)
                    variance = sum((x - average) ** 2 for x in H_data) / len(H_data)
                    std = variance ** 0.5  + average # Standard deviation + average
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
                    for i,_ in enumerate(calm_values):            
                        #calm_values[i][hour]['H'], onde i é os dias selecionados, hour é cada minuto do dia e 'H' é os valores de H das estações
                        H_data.append(calm_values[i][hour]['H'])
                    average = sum(H_data)/len(self.selected_calm_dates)
                    variance = sum((x - average) ** 2 for x in H_data) / len(H_data)
                    std = average -  variance ** 0.5  # Standard deviation - average
                    calm_avgMstd_H.append(std)
                except Exception:
                    calm_avgMstd_H.append(None)

            return calm_avgMstd_H
    
    def calculate_calm_average_Z(self):
        # Calculate the average for calm days using selected_calm_dates./Calcular a média para os dias calmos usando selected_calm_dates.
        calm_averages_Z = []
        calm_values = self.get_cal_datas(self.selected_calm_dates) 
        for hour in range(1440):
            try:
                Z_data = []
                for i,_ in enumerate(calm_values):            
                    #calm_values[i][hour]['H'], onde i é os dias selecionados, hour é cada minuto do dia e 'H' é os valores de H das estações
                    Z_data.append(calm_values[i][hour]['Z'])
                average = sum(Z_data)/len(self.selected_calm_dates)
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
                    for i,_ in enumerate(calm_values):            
                        #calm_values[i][hour]['H'], onde i é os dias selecionados, hour é cada minuto do dia e 'H' é os valores de H das estações
                        Z_data.append(calm_values[i][hour]['Z'])
                    average = sum(Z_data)/len(self.selected_calm_dates)
                    variance = sum((x - average) ** 2 for x in Z_data) / len(Z_data)
                    std = variance ** 0.5  + average # Standard deviation + average
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
                    for i,_ in enumerate(calm_values):            
                        #calm_values[i][hour]['H'], onde i é os dias selecionados, hour é cada minuto do dia e 'H' é os valores de H das estações
                        Z_data.append(calm_values[i][hour]['Z'])
                    average = sum(Z_data)/len(self.selected_calm_dates)
                    variance = sum((x - average) ** 2 for x in Z_data) / len(Z_data)
                    std = average -  variance ** 0.5  # Standard deviation - average
                    calm_avgMstd_Z.append(std)
                except Exception:
                    calm_avgMstd_Z.append(None)

            return calm_avgMstd_Z
    
    def calculate_calm_average_X(self):
        # Calculate the average for calm days using selected_calm_dates./Calcular a média para os dias calmos usando selected_calm_dates.
        calm_averages_X = []
        calm_values = self.get_cal_datas(self.selected_calm_dates) 
        for hour in range(1440):
            try:
                X_data = []
                for i,_ in enumerate(calm_values):            
                    #calm_values[i][hour]['H'], onde i é os dias selecionados, hour é cada minuto do dia e 'H' é os valores de H das estações
                    X_data.append(calm_values[i][hour]['X'])
                average = sum(X_data)/len(self.selected_calm_dates)
                calm_averages_X.append(average)
            except Exception:
                calm_averages_X.append(None)

        return calm_averages_X
    
    # Average + Std Dev
    def calculate_calm_averagePstd_X(self):
            calm_avgPstd_X = []
            calm_values = self.get_cal_datas(self.selected_calm_dates) 
            for hour in range(1440):
                try:
                    X_data = []
                    for i,_ in enumerate(calm_values):            
                        #calm_values[i][hour]['H'], onde i é os dias selecionados, hour é cada minuto do dia e 'H' é os valores de H das estações
                        X_data.append(calm_values[i][hour]['X'])
                    average = sum(X_data)/len(self.selected_calm_dates)
                    variance = sum((x - average) ** 2 for x in X_data) / len(X_data)
                    std = variance ** 0.5  + average # Standard deviation + average
                    calm_avgPstd_X.append(std)
                except Exception:
                    calm_avgPstd_X.append(None)

            return calm_avgPstd_X
    
    # Average - Std Dev
    def calculate_calm_averageMstd_X(self):
            calm_avgMstd_X = []
            calm_values = self.get_cal_datas(self.selected_calm_dates) 
            for hour in range(1440):
                try:
                    X_data = []
                    for i,_ in enumerate(calm_values):            
                        #calm_values[i][hour]['H'], onde i é os dias selecionados, hour é cada minuto do dia e 'H' é os valores de H das estações
                        X_data.append(calm_values[i][hour]['X'])
                    average = sum(X_data)/len(self.selected_calm_dates)
                    variance = sum((x - average) ** 2 for x in X_data) / len(X_data)
                    std = average -  variance ** 0.5  # Standard deviation - average
                    calm_avgMstd_X.append(std)
                except Exception:
                    calm_avgMstd_X.append(None)

            return calm_avgMstd_X
    
    def calculate_calm_average_Y(self):
        # Calculate the average for calm days using selected_calm_dates./Calcular a média para os dias calmos usando selected_calm_dates.
        calm_averages_Y = []
        calm_values = self.get_cal_datas(self.selected_calm_dates) 
        for hour in range(1440):
            try:
                Y_data = []
                for i,_ in enumerate(calm_values):            
                    #calm_values[i][hour]['H'], onde i é os dias selecionados, hour é cada minuto do dia e 'H' é os valores de H das estações
                    Y_data.append(calm_values[i][hour]['Y'])
                average = sum(Y_data)/len(self.selected_calm_dates)
                calm_averages_Y.append(average)
            except Exception:
                calm_averages_Y.append(None)

        return calm_averages_Y
    
    # Average + Std Dev
    def calculate_calm_averagePstd_Y(self):
            calm_avgPstd_Y = []
            calm_values = self.get_cal_datas(self.selected_calm_dates) 
            for hour in range(1440):
                try:
                    Y_data = []
                    for i,_ in enumerate(calm_values):            
                        #calm_values[i][hour]['H'], onde i é os dias selecionados, hour é cada minuto do dia e 'H' é os valores de H das estações
                        Y_data.append(calm_values[i][hour]['Y'])
                    average = sum(Y_data)/len(self.selected_calm_dates)
                    variance = sum((x - average) ** 2 for x in Y_data) / len(Y_data)
                    std = variance ** 0.5  + average # Standard deviation + average
                    calm_avgPstd_Y.append(std)
                except Exception:
                    calm_avgPstd_Y.append(None)

            return calm_avgPstd_Y
    
    # Average - Std Dev
    def calculate_calm_averageMstd_Y(self):
            calm_avgMstd_Y = []
            calm_values = self.get_cal_datas(self.selected_calm_dates) 
            for hour in range(1440):
                try:
                    Y_data = []
                    for i,_ in enumerate(calm_values):            
                        #calm_values[i][hour]['H'], onde i é os dias selecionados, hour é cada minuto do dia e 'H' é os valores de H das estações
                        Y_data.append(calm_values[i][hour]['Y'])
                    average = sum(Y_data)/len(self.selected_calm_dates)
                    variance = sum((x - average) ** 2 for x in Y_data) / len(Y_data)
                    std = average -  variance ** 0.5  # Standard deviation - average
                    calm_avgMstd_Y.append(std)
                except Exception:
                    calm_avgMstd_Y.append(None)

            return calm_avgMstd_Y

    def calculate_calm_average_D(self):
        # Calculate the average for calm days using selected_calm_dates./Calcular a média para os dias calmos usando selected_calm_dates.
        calm_averages_D = []
        calm_values = self.get_cal_datas(self.selected_calm_dates) 
        for hour in range(1440):
            try:
                D_data = []
                for i,_ in enumerate(calm_values):            
                    #calm_values[i][hour]['H'], onde i é os dias selecionados, hour é cada minuto do dia e 'H' é os valores de H das estações
                    D_data.append(calm_values[i][hour]['D'])
                average = sum(D_data)/len(self.selected_calm_dates)
                calm_averages_D.append(average)
            except Exception:
                calm_averages_D.append(None)

        return calm_averages_D
    
    # Average + Std Dev
    def calculate_calm_averagePstd_D(self):
            calm_avgPstd_D = []
            calm_values = self.get_cal_datas(self.selected_calm_dates) 
            for hour in range(1440):
                try:
                    D_data = []
                    for i,_ in enumerate(calm_values):            
                        #calm_values[i][hour]['H'], onde i é os dias selecionados, hour é cada minuto do dia e 'H' é os valores de H das estações
                        D_data.append(calm_values[i][hour]['D'])
                    average = sum(D_data)/len(self.selected_calm_dates)
                    variance = sum((x - average) ** 2 for x in D_data) / len(D_data)
                    std = variance ** 0.5  + average # Standard deviation + average
                    calm_avgPstd_D.append(std)
                except Exception:
                    calm_avgPstd_D.append(None)

            return calm_avgPstd_D
    
    # Average - Std Dev
    def calculate_calm_averageMstd_D(self):
            calm_avgMstd_D = []
            calm_values = self.get_cal_datas(self.selected_calm_dates) 
            for hour in range(1440):
                try:
                    D_data = []
                    for i,_ in enumerate(calm_values):            
                        #calm_values[i][hour]['H'], onde i é os dias selecionados, hour é cada minuto do dia e 'H' é os valores de H das estações
                        D_data.append(calm_values[i][hour]['D'])
                    average = sum(D_data)/len(self.selected_calm_dates)
                    variance = sum((x - average) ** 2 for x in D_data) / len(D_data)
                    std = average -  variance ** 0.5  # Standard deviation - average
                    calm_avgMstd_D.append(std)
                except Exception:
                    calm_avgMstd_D.append(None)

            return calm_avgMstd_D
    
    def calculate_calm_average_F(self):
        # Calculate the average for calm days using selected_calm_dates./Calcular a média para os dias calmos usando selected_calm_dates.
        calm_averages_F = []
        calm_values = self.get_cal_datas(self.selected_calm_dates) 
        for hour in range(1440):
            try:
                F_data = []
                for i,_ in enumerate(calm_values):            
                    #calm_values[i][hour]['H'], onde i é os dias selecionados, hour é cada minuto do dia e 'H' é os valores de H das estações
                    F_data.append(calm_values[i][hour]['F'])
                average = sum(F_data)/len(self.selected_calm_dates)
                calm_averages_F.append(average)
            except Exception:
                calm_averages_F.append(None)

        return calm_averages_F
    
    # Average + Std Dev
    def calculate_calm_averagePstd_F(self):
            calm_avgPstd_F = []
            calm_values = self.get_cal_datas(self.selected_calm_dates) 
            for hour in range(1440):
                try:
                    F_data = []
                    for i,_ in enumerate(calm_values):            
                        #calm_values[i][hour]['H'], onde i é os dias selecionados, hour é cada minuto do dia e 'H' é os valores de H das estações
                        F_data.append(calm_values[i][hour]['F'])
                    average = sum(F_data)/len(self.selected_calm_dates)
                    variance = sum((x - average) ** 2 for x in F_data) / len(F_data)
                    std = variance ** 0.5  + average # Standard deviation + average
                    calm_avgPstd_F.append(std)
                except Exception:
                    calm_avgPstd_F.append(None)

            return calm_avgPstd_F
    
    # Average - Std Dev
    def calculate_calm_averageMstd_F(self):
            calm_avgMstd_F = []
            calm_values = self.get_cal_datas(self.selected_calm_dates) 
            for hour in range(1440):
                try:
                    F_data = []
                    for i,_ in enumerate(calm_values):            
                        #calm_values[i][hour]['H'], onde i é os dias selecionados, hour é cada minuto do dia e 'H' é os valores de H das estações
                        F_data.append(calm_values[i][hour]['F'])
                    average = sum(F_data)/len(self.selected_calm_dates)
                    variance = sum((x - average) ** 2 for x in F_data) / len(F_data)
                    std = average -  variance ** 0.5  # Standard deviation - average
                    calm_avgMstd_F.append(std)
                except Exception:
                    calm_avgMstd_F.append(None)

            return calm_avgMstd_F
    
    def calculate_calm_average_I(self):
        # Calculate the average for calm days using selected_calm_dates./Calcular a média para os dias calmos usando selected_calm_dates.
        calm_averages_I = []
        calm_values = self.get_cal_datas(self.selected_calm_dates) 
        for hour in range(1440):
            try:
                I_data = []
                for i,_ in enumerate(calm_values):            
                    #calm_values[i][hour]['H'], onde i é os dias selecionados, hour é cada minuto do dia e 'H' é os valores de H das estações
                    I_data.append(calm_values[i][hour]['I'])
                average = sum(I_data)/len(self.selected_calm_dates)
                calm_averages_I.append(average)
            except Exception:
                calm_averages_I.append(None)

        return calm_averages_I
    
    # Average + Std Dev
    def calculate_calm_averagePstd_I(self):
            calm_avgPstd_I = []
            calm_values = self.get_cal_datas(self.selected_calm_dates) 
            for hour in range(1440):
                try:
                    I_data = []
                    for i,_ in enumerate(calm_values):            
                        #calm_values[i][hour]['H'], onde i é os dias selecionados, hour é cada minuto do dia e 'H' é os valores de H das estações
                        I_data.append(calm_values[i][hour]['I'])
                    average = sum(I_data)/len(self.selected_calm_dates)
                    variance = sum((x - average) ** 2 for x in I_data) / len(I_data)
                    std = variance ** 0.5  + average # Standard deviation + average
                    calm_avgPstd_I.append(std)
                except Exception:
                    calm_avgPstd_I.append(None)

            return calm_avgPstd_I
    
    # Average - Std Dev
    def calculate_calm_averageMstd_I(self):
            calm_avgMstd_I = []
            calm_values = self.get_cal_datas(self.selected_calm_dates) 
            for hour in range(1440):
                try:
                    I_data = []
                    for i,_ in enumerate(calm_values):            
                        #calm_values[i][hour]['H'], onde i é os dias selecionados, hour é cada minuto do dia e 'H' é os valores de H das estações
                        I_data.append(calm_values[i][hour]['I'])
                    average = sum(I_data)/len(self.selected_calm_dates)
                    variance = sum((x - average) ** 2 for x in I_data) / len(I_data)
                    std = average -  variance ** 0.5  # Standard deviation - average
                    calm_avgMstd_I.append(std)
                except Exception:
                    calm_avgMstd_I.append(None)

            return calm_avgMstd_I
    
    def calculate_calm_average_G(self):
        # Calculate the average for calm days using selected_calm_dates./Calcular a média para os dias calmos usando selected_calm_dates.
        calm_averages_G = []
        calm_values = self.get_cal_datas(self.selected_calm_dates) 
        for hour in range(1440):
            try:
                G_data = []
                for i,_ in enumerate(calm_values):            
                    #calm_values[i][hour]['H'], onde i é os dias selecionados, hour é cada minuto do dia e 'H' é os valores de H das estações
                    G_data.append(calm_values[i][hour]['G'])
                average = sum(G_data)/len(self.selected_calm_dates)
                calm_averages_G.append(average)
            except Exception:
                calm_averages_G.append(None)

        return calm_averages_G
    
    # Average + Std Dev
    def calculate_calm_averagePstd_G(self):
            calm_avgPstd_G = []
            calm_values = self.get_cal_datas(self.selected_calm_dates) 
            for hour in range(1440):
                try:
                    G_data = []
                    for i,_ in enumerate(calm_values):            
                        #calm_values[i][hour]['H'], onde i é os dias selecionados, hour é cada minuto do dia e 'H' é os valores de H das estações
                        G_data.append(calm_values[i][hour]['I'])
                    average = sum(G_data)/len(self.selected_calm_dates)
                    variance = sum((x - average) ** 2 for x in G_data) / len(G_data)
                    std = variance ** 0.5  + average # Standard deviation + average
                    calm_avgPstd_G.append(std)
                except Exception:
                    calm_avgPstd_G.append(None)

            return calm_avgPstd_G
    
    # Average - Std Dev
    def calculate_calm_averageMstd_G(self):
            calm_avgMstd_G = []
            calm_values = self.get_cal_datas(self.selected_calm_dates) 
            for hour in range(1440):
                try:
                    G_data = []
                    for i,_ in enumerate(calm_values):            
                        #calm_values[i][hour]['H'], onde i é os dias selecionados, hour é cada minuto do dia e 'H' é os valores de H das estações
                        G_data.append(calm_values[i][hour]['I'])
                    average = sum(G_data)/len(self.selected_calm_dates)
                    variance = sum((x - average) ** 2 for x in G_data) / len(G_data)
                    std = average -  variance ** 0.5  # Standard deviation - average
                    calm_avgMstd_G.append(std)
                except Exception:
                    calm_avgMstd_G.append(None)

            return calm_avgMstd_G


    # Retrieves the data for a given station and date from the corresponding file
    def get_data(self, day, station, network_station):
        if isinstance(day, QDate):
            day = day.toPyDate()

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
             return [{'D':None, 'H':None, 'Z':None, 'I':None, 'F':None, 'G': None, 'X': None, 'Y': None}] * 1440

        try: # Differentiates Intermagnet's VSS from Embrace's VSS
            self.st = 'VSS' if (self.st == 'VSI') or (self.st == 'VSE') else self.st
            for line in lines:
                if line == '':
                    continue 
                if is_header: # Finds the H, X, Y, F, and G values in the .min files
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

                else: # Removes invalid data
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
            #tk.messagebox.showinfo(self.util.dict_language[self.lang]["mgbox_error"], f'{self.util.dict_language[self.lang]["mgbox_error_info_ad"]}: {error}')
            QMessageBox.critical(
                None,
                self.util.dict_language[self.lang]["mgbox_error"],
                error
            )
            return data