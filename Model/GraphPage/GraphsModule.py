from Model.Custom.CustomttkFrame import ScrollableFrame
import os
from datetime import datetime
import math
import re
from General.util import Util
from datetime import timedelta
from PyQt5.QtWidgets import (
    QMessageBox, QDialog, QVBoxLayout, QLabel, QCheckBox, QPushButton, QFileDialog, QWidget
)
from PyQt5.QtCore import Qt, QDate
from pyIGRF import igrf_value

class GraphsModule():
    def __init__(self, language):
        self.lang = language
        
        self.stations = None
        self.date = None
        self.all_data = None
        self.main_downloaded_stations = None
        self.main_downloaded_stations_dict = None

        self.util = Util()

    # Searches for downloaded stations from EMBRACE and INTERMAGNET data folders
    def search_stations_downloaded(self, year, drive_location="C:\\"):
        current_year = datetime.now().year
        main_downloaded_stations = set()
        data_with_stations = {}

        for year in range(1990, current_year+1):
            embrace_folder_path = rf'{drive_location}Magnetometer\EMBRACE\{str(year)}'
            intermagnet_folder_path = rf'{drive_location}Magnetometer\INTERMAGNET\{str(year)}'

            if os.path.exists(embrace_folder_path):
                embrace_stations = os.listdir(embrace_folder_path)
                if embrace_stations:
                    for station in embrace_stations:
                        data_with_stations[station] = ['EMBRACE']
                        main_downloaded_stations.add(station)

            if os.path.exists(intermagnet_folder_path):
                intermagnet_stations = os.listdir(intermagnet_folder_path)
                if intermagnet_stations:
                    for station in intermagnet_stations:
                        data_with_stations[station] = ['INTERMAGNET']
                        main_downloaded_stations.add(station)

        if os.path.exists('readme_stations.txt'):
            with open('readme_stations.txt','r') as file:
                lines = file.readlines()
                lines.pop(0)
                for line in lines:
                    l = re.split(r'\s{2,}', line)
                    try:
                        if l[0] == 'VSS' and l[4] == 'INTERMAGNET\n': st = 'VSI' 
                        elif l[0] == 'VSS' and l[4] == 'EMBRACE\n': st = 'VSE'
                        else: st = l[0]

                        if st in main_downloaded_stations:
                            long  = float(l[2])
                            lat = float(l[3])
                            if long > 180: long = long - 360.0
                            local_hour = long/15
                            local_min = local_hour - int(local_hour)
                            local_hour -= local_min
                            local_min = int(local_min * 60)

                            data_with_stations[f'{st}'].append(long)
                            #if st == "SJC": print(data_with_stations[f'{st}'][0])
                            data_with_stations[f'{st}'].append(lat)
                            data_with_stations[f'{st}'].append(local_hour * -1)
                            data_with_stations[f'{st}'].append(local_min * -1)
                    except Exception as error:
                        print('erro adquirindo dados do readme', error)
                        
        main_downloaded_stations = sorted(list(main_downloaded_stations), key=str.lower)

        for i in range(0, len(main_downloaded_stations)):
            result = igrf_value(data_with_stations[main_downloaded_stations[i]][2], data_with_stations[main_downloaded_stations[i]][1], 300, year)
            dip = -math.degrees(math.atan((math.tan(math.radians(result[1]))/2)))
            main_downloaded_stations[i] = f"{main_downloaded_stations[i]} ({data_with_stations[main_downloaded_stations[i]][2]:.5f}, {data_with_stations[main_downloaded_stations[i]][1]:.5f}, {dip:.5f})"
        return main_downloaded_stations, data_with_stations
    
    # Retrieves the data for a given station and date from the corresponding file
    def get_data(self, day, station, network_station):
        day = datetime.combine(day, datetime.min.time())
        initial_day = day
        self.st = station
        path_station = os.path.join(
            self.lcl_downloaded, "Magnetometer", network_station, str(day.year),
            self.st, f"{self.st.lower()}{day.year}{day.month:02}{day.day:02}min.min"
        )
        
        data = {}
        day_dict = {}

        if not os.path.exists(path_station):
            for _ in range(1440):
                day_dict[f'{day.hour}:{day.minute}'] = {'D': None, 'H': None, 'Z': None, 'I': None, 'F': None, 'G': None, 'X': None, 'Y': None}
                day += timedelta(minutes=1)

            data[f'{initial_day.day}/{initial_day.month}/{initial_day.year}'] = day_dict
            return data
        
        self.st = 'VSS' if self.st in {'VSI', 'VSE'} else self.st

        try:
            with open(path_station, "r") as file:
                lines = file.readlines()

            archive_case = None
            for header, line in enumerate(lines):
                if line.find('H(nT)') != -1:
                    archive_case = 'embrace:h'
                    header_pos = header
                    break
                if line.find(f'{self.st}X') != -1 and line.find(f'{self.st}F') != -1:
                    archive_case = 'intermagnet:x,y,f'
                    header_pos = header
                    break
                if line.find(f'{self.st}X') != -1 and line.find(f'{self.st}G') != -1:
                    archive_case = 'intermagnet:x,y,g'
                    header_pos = header
                    break
                if line.find(f'{self.st}H') != -1:
                    archive_case = 'intermagnet:h'
                    header_pos = header
                    break
            
            if not archive_case:
                return None

            for header, line in enumerate(lines):
                if not line.strip() or header <= header_pos:
                    continue

                data_dict = {}
                separated_data = line.split()

                match archive_case:
                    case 'embrace:h':
                        if len(separated_data) < 9: 
                            data_dict = {'D': None, 'H': None, 'Z': None, 'I': None, 'F': None}
                        else:
                            data_dict = {
                                'D': self._parse_float(separated_data[5]),
                                'H': self._parse_float(separated_data[6]),
                                'Z': self._parse_float(separated_data[7]),
                                'I': self._parse_float(separated_data[8]),
                                'F': self._parse_float(separated_data[9]),
                            }
                    case 'intermagnet:x,y,f':
                        if len(separated_data) < 6: 
                            data_dict = {'H': None, 'X': None, 'Y': None, 'Z': None, 'F': None}
                        else:
                            x, y = self._parse_float(separated_data[3]), self._parse_float(separated_data[4])
                            data_dict = {
                                'H': math.sqrt(x**2 + y**2) if x is not None and y is not None else None,
                                'X': x, 'Y': y,
                                'Z': self._parse_float(separated_data[5]),
                                'F': self._parse_float(separated_data[6]),
                            }
                    case 'intermagnet:x,y,g':
                        if len(separated_data) < 6: 
                            data_dict = {'H': None, 'X': None, 'Y': None, 'Z': None, 'G': None}
                        else:
                            x, y = self._parse_float(separated_data[3]), self._parse_float(separated_data[4])
                            data_dict = {
                                'H': math.sqrt(x**2 + y**2) if x is not None and y is not None else None,
                                'X': x, 'Y': y,
                                'Z': self._parse_float(separated_data[5]),
                                'G': self._parse_float(separated_data[6]),
                            }
                    case 'intermagnet:h':
                        if len(separated_data) < 6: 
                            data_dict = {'H': None, 'D': None, 'Z': None, 'F': None}
                        else:
                            data_dict = {
                                'H': self._parse_float(separated_data[3]),
                                'D': self._parse_float(separated_data[4]),
                                'Z': self._parse_float(separated_data[5]),
                                'F': self._parse_float(separated_data[6]),
                            }

                day_dict[f"{day.hour}:{day.minute}"] = data_dict
                day += timedelta(minutes=1)

            data[f'{initial_day.day}/{initial_day.month}/{initial_day.year}'] = day_dict
            return data
        except Exception as error:
            print(error)
            QMessageBox.information(
                None,
                self.util.dict_language[self.lang]["mgbox_error"], 
                f'{self.util.dict_language[self.lang]["mgbox_error_info_ad"]}: {error}'
            )
            return data
        
    # verify if it's a invalid data
    def _parse_float(self, value):
        try:
            return float(value) if float(value) != 99999.00 else None
        except ValueError:
            return None

    # collects data from a period
    def get_stations_data(self):
        all_data = {}

        for station in self.stations:
            station = station.split()[0]
            # Converter apenas se for QDate
            if isinstance(self.start_date, QDate):
                current_date = self.start_date.toPyDate()
            else:
                current_date = self.start_date

            if isinstance(self.end_date, QDate):
                end_date = self.end_date.toPyDate()
            else:
                end_date = self.end_date
            station_data = {}
            while current_date < end_date: 
                single_data = self.get_data(current_date, station, self.data_with_stations[f'{station}'][0])
                station_data.update(single_data)
                current_date += timedelta(days=1)
            all_data[station] = station_data
        return all_data
    
    # collects data from all dates selected
    def get_especific_dates(self, selected_dates, station):   
        station_data = {}
        station = station.split()[0]
        for date in selected_dates:
            data = self.get_data(date, station, self.data_with_stations[f'{station}'][0])
            station_data.update(data)
        return station_data

    # calculates midnight avarage for delta calculation
    def calculate_midnight_average(self, type):
        # gets data to search midnight average 
        days_data = {}
        for station in self.stations:
            station = station.split()[0]
            dates = []
            for date in self.slct_dates:
                dt = datetime.combine(date, datetime.min.time()) + timedelta(hours=self.data_with_stations[station][3], minutes=self.data_with_stations[station][4])
                dates.append(dt.replace(hour=0, minute=0))
            especific_data = self.get_especific_dates(dates, station)
            days_data[station] = especific_data

        # calculate midnight average
        delta = []
        self.info_time = {}
        for station in self.stations:
            station = station.split()[0]
            if self.can_plot:
                midnight_data = self.take_midnight_data(type, days_data, station)
            if not midnight_data: 
                delta.append(0)
            else:
                station_delta = sum(midnight_data) / len(self.slct_dates) if len(self.slct_dates) != 0 else 0
                delta.append(station_delta)

        return delta

    # Calculate midnight avarage for reference calculation
    def calculate_midnight_average_reference(self, type):
        # gets data to search midnight average 
        all_data = {}
        for station in self.stations:
            station = station.split()[0]
            dates = []
            for date in self.slct_dates:
                dt = datetime.combine(date, datetime.min.time()) + timedelta(hours=self.data_with_stations[station][3], minutes=self.data_with_stations[station][4])
                dates.append(dt.replace(hour=0, minute=0))
            especific_data = self.get_especific_dates(dates, station)
            all_data[station] = especific_data

        # calculate midnight average
        midnight_data = []
        self.info_time = {}
        for station in self.stations:
            midnight_data.extend(self.take_midnight_data(type, all_data, station))
        delta = sum(midnight_data) / (len(self.slct_dates) * len(self.stations)) if len(self.slct_dates) != 0 else 0

        return delta
    
    # Gets avarage from 
    def calculate_reference(self, type):
        calm_values = {station: self.get_especific_dates(self.slct_dates, station) for station in self.stations}

        calm_averages = []
        time = datetime(year=2025, month=2, day=7, hour=0, minute=0)
        end_time = datetime(year=2025, month=2, day=8, hour=0, minute=0)

        while time < end_time:
            H_data = []

            for station in self.stations:
                station = station.split()[0]
                for date in self.slct_dates:
                    H_value = calm_values.get(station, None).get(f'{date.day}/{date.month}/{date.year}', None).get(f'{time.hour}:{time.minute}', None).get(type)
                    if H_value is not None:
                        H_data.append(H_value)

            average = sum(H_data) / len(H_data) if H_data else None
            calm_averages.append(average)

            time += timedelta(minutes=1)
        return calm_averages

    # takes all midnights data from a station in selected dates
    def take_midnight_data(self, type, data_info, station):
        try:
            station = station.split()[0]
            midnight_data = []
            self.info_time[station] = []
            for date in self.slct_dates:
                day = datetime.combine(date, datetime.min.time()) + timedelta(hours=self.data_with_stations[station][3], minutes=self.data_with_stations[station][4])
                data = data_info[station][f'{day.day}/{day.month}/{day.year}'][f'{day.hour}:{day.minute}'][type]
                # add to data in time to info dict
                string_info = f'{day.year}-{day.month:02}-{day.day:02}: Hour: {day.hour} Minute: {day.minute}'
                for info_type in self.slct_types: 
                    if 'reference' not in info_type:
                        base_type = info_type.replace('d','')
                        string_info+=f' - {info_type}: {data_info[station][f'{day.day}/{day.month}/{day.year}'][f'{day.hour}:{day.minute}'][base_type]} '
                self.info_time[station].append(string_info)

                if data is not None: 
                    midnight_data.append(data)   
                else:
                    QMessageBox.information(
                        None,
                        self.util.dict_language[self.lang]["mgbox_error"], 
                        f'{self.util.dict_language[self.lang]["mgbox_error_inval_info"]} {date.day:02}/{date.month:02}/{date.year} - {station} - {type}')
                    self.slct_dates.remove(date)
                    # self.cal_selection.calevent_remove(date=date) # Remover ou adaptar para PyQt5
                    self.can_plot = False
                    return
                
            return midnight_data
        except Exception as error:
            print(f'take_midnight_data: {error}')
            QMessageBox.information(
                None,
                self.util.dict_language[self.lang]["mgbox_error"], 
                f'{self.util.dict_language[self.lang]["mgbox_error_noinfo_period"]} {day.day:02}/{day.month:02}/{day.year} - {station} - {type}'
            )
            self.can_plot = False

    # inform type average and given hours for calm days
    def inform_graph(self, selected_types, avarage_types):
        inform_window = QDialog(self.root)
        inform_window.setWindowTitle('info_graph')
        inform_window.setModal(True)
        inform_window.resize(800, 600)

        layout = QVBoxLayout(inform_window)
        frame = ScrollableFrame(inform_window, 800)
        layout.addWidget(frame)

        text_for_lbl = ''
        lbl_text = QLabel()
        lbl_text.setWordWrap(True)
        frame.inner_layout.addWidget(lbl_text)
        
        for station in self.stations:
            station = station.split()[0]
            text_for_lbl += f'\n\n{station}:\n'
            for type in selected_types:
                text_for_lbl += f'{type}: {avarage_types[station][type]}\n'

            text_for_lbl += 'Hours got from Quite days:\n'
            if self.info_time:
                text_for_lbl += '\n'.join(self.info_time[station])

        lbl_text.setText(text_for_lbl)
        inform_window.exec_()

    # calculate avarage for many data's type 
    def calculate_type_averages(self, slct_types, slct_stations):
        try:
            avarage_type = {}
            for station in slct_stations:
                station = station.split()[0]
                avarage_type[station] = {}
                if isinstance(self.start_date, QDate):
                    self.start_date = self.start_date.toPyDate()
                date = datetime.combine(self.start_date, datetime.min.time())
                for type in slct_types:
                    period_data = [0]
                    date = datetime.combine(date, datetime.min.time())
                    while date < datetime.combine(self.end_date, datetime.min.time()):
                        data = self.all_data[station][f'{date.day}/{date.month}/{date.year}'][f'{date.hour}:{date.minute}'][type]
                        if data != None: 
                            period_data.append(data)
                        date += timedelta(minutes=1)
                        
                    avarage = sum(period_data) / len(self.all_data[station]) * 1440
                    avarage_type[station].update({type: avarage})
                    date = self.start_date
            return avarage_type
        except KeyError as error:
            print(f'calculate_type_averages: {error}')
            QMessageBox.information(
                None,
                self.util.dict_language[self.lang]["mgbox_error"],
                f'{self.util.dict_language[self.lang]["mgbox_error_type"]} {station}({error})'
            )
            return None

    # validate given dates and format them into datetime 
    def format_dates(self, start, end):
        #start_date = datetime.strptime(start, r'%d/%m/%Y')
        #end_date = datetime.strptime(end, r'%d/%m/%Y')
        start_date = start
        end_date = end
        if start_date > end_date:
            QMessageBox.information(
                None,
                self.util.dict_language[self.lang]["mgbox_error"],
                self.util.dict_language[self.lang]["mgbox_error_dt_dif"]
            )
            return False, False
        return start_date, end_date

    # gets type measure accordingly to the given data type
    def get_measure(self, plot_type):  
        nt_unit = {'dH','H','Reference-H','dZ','Z','Reference-Z','dF','F','Reference-F','dG','G','Reference-G','dX','X','Reference-X','dY','Y','Reference-Y'}
        deg_unit = {'dD','D','Reference-D','dI','I','Reference-I'}

        has_nt = any(type in nt_unit for type in plot_type)
        has_deg = any(type in deg_unit for type in plot_type)

        if has_nt and has_deg: return 'Undefined'
        if has_nt: return 'nT'
        if has_deg: return 'Deg'

    # verify if all inputs has something selected
    def verify_inputs(self, station_selected=True, type_selected=True):
        if not station_selected:
            QMessageBox.information(
                None,
                self.util.dict_language[self.lang]["mgbox_error"],
                self.util.dict_language[self.lang]["mgbox_error_st"]
            )
            return False
        if not type_selected:
            QMessageBox.information(
                None,
                self.util.dict_language[self.lang]["mgbox_error"],
                self.util.dict_language[self.lang]["mgbox_error_dt_type"]
            )
            return False
        return True

    # creates the view to export info from graph
    def create_exporter_level_top(self, event, slct_types, is_difference = False):
        if hasattr(event, "button") and event.button == Qt.RightButton:
            self.temp_window = QDialog(self.root)
            self.temp_window.setWindowTitle('Plot Downloader')
            self.temp_window.resize(200, 600)
            layout = QVBoxLayout(self.temp_window)

            # Dicionário para armazenar os checkboxes
            self.checkboxes = {}

            for idx, type_name in enumerate(slct_types):
                cb = QCheckBox(type_name)
                layout.addWidget(cb)
                self.checkboxes[type_name] = cb

            btn_confirm = QPushButton(self.util.dict_language[self.lang]['btn_confirm'])
            btn_confirm.clicked.connect(lambda: self.export_file(is_difference))
            layout.addWidget(btn_confirm)

            self.temp_window.setLayout(layout)
            self.temp_window.setModal(True)
            self.temp_window.exec_()

    # reads all info and creates custom file
    def export_file(self, is_difference=False):
        save_file_path = QFileDialog.getExistingDirectory(self.temp_window, "Select Directory")
        if not save_file_path:
            return

        all_types = [t for t, cb in self.checkboxes.items() if cb.isChecked()]
        header = 'Hour    ' + '          '.join(all_types)

        if not is_difference:
            for station in self.stations:
                for day, times in self.all_data[station].items():
                    t = timedelta(hours=0, minutes=0)
                    lines = ''
                    for time in times:
                        hh = t.total_seconds() / 3600
                        lines += f'{hh:.2f}    '
                        t += timedelta(minutes=1)

                        for type in all_types:
                            lines += f'{self.all_data.get(station, "None").get(day, "None").get(time, "None").get(type, "None")}    '
                        lines += '\n'

                    date = day.split('/')

                    file = open(os.path.join(save_file_path, f'{station.lower()}{date[2]}{int(date[1]):02}{int(date[0]):02}.txt'), 'w+')
                    file.write(header+'\n'+lines)
                    file.close()
        else:
            for day, times in self.diff_data.items():
                t = timedelta(hours=0, minutes=0)
                lines = ''
                for time in times:
                    hh = t.total_seconds() / 3600
                    lines += f'{hh:.2f}    '
                    t += timedelta(minutes=1)

                    for type in all_types:
                        lines += f'{self.diff_data.get(day, None).get(time, None).get(type, None)}    '
                    lines += '\n'

                date = day.split('/')

                file = open(os.path.join(save_file_path, f'{self.min_station.lower()}-{self.sub_station.lower()}{date[2]}{int(date[1]):02}{int(date[0]):02}.txt'), 'w+')
                file.write(header+'\n'+lines)
                file.close()
                    
        self.temp_window.accept()