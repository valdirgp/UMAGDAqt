from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QMessageBox, QDialog,
    QCheckBox, QPushButton, QFileDialog, QScrollArea, QFrame, QGridLayout
)
from datetime import datetime, timedelta
from General.util import Util
import os, math, re


class GraphsModule:
    def __init__(self, language, root=None):
        self.lang = language
        self.root = root  # janela principal (QMainWindow ou QWidget)
        self.stations = None
        self.date = None
        self.all_data = None
        self.main_downloaded_stations = None
        self.main_downloaded_stations_dict = None

        self.util = Util()

    # ------------------------
    # Substituindo messagebox
    # ------------------------
    def show_message(self, title, text):
        QMessageBox.information(self.root, title, text)

    # ------------------------
    # Funções originais
    # ------------------------
    def search_stations_downloaded(self, drive_location="C:\\"):
        current_year = datetime.now().year
        main_downloaded_stations = set()
        data_with_stations = {}

        for year in range(1990, current_year + 1):
            embrace_folder_path = rf'{drive_location}Magnetometer\EMBRACE\{str(year)}'
            intermagnet_folder_path = rf'{drive_location}Magnetometer\INTERMAGNET\{str(year)}'

            if os.path.exists(embrace_folder_path):
                embrace_stations = os.listdir(embrace_folder_path)
                for station in embrace_stations:
                    data_with_stations[station] = ['EMBRACE']
                    main_downloaded_stations.add(station)

            if os.path.exists(intermagnet_folder_path):
                intermagnet_stations = os.listdir(intermagnet_folder_path)
                for station in intermagnet_stations:
                    data_with_stations[station] = ['INTERMAGNET']
                    main_downloaded_stations.add(station)

        if os.path.exists('readme_stations.txt'):
            with open('readme_stations.txt', 'r') as file:
                lines = file.readlines()
                lines.pop(0)
                for line in lines:
                    l = re.split(r'\s{2,}', line)
                    try:
                        if l[0] == 'VSS' and l[4] == 'INTERMAGNET\n':
                            st = 'VSI'
                        elif l[0] == 'VSS' and l[4] == 'EMBRACE\n':
                            st = 'VSE'
                        else:
                            st = l[0]

                        if st in main_downloaded_stations:
                            long = float(l[2])
                            lat = float(l[3])
                            if long > 180:
                                long -= 360.0
                            local_hour = long / 15
                            local_min = local_hour - int(local_hour)
                            local_hour -= local_min
                            local_min = int(local_min * 60)

                            data_with_stations[f'{st}'].append(long)
                            data_with_stations[f'{st}'].append(lat)
                            data_with_stations[f'{st}'].append(local_hour * -1)
                            data_with_stations[f'{st}'].append(local_min * -1)
                    except Exception as error:
                        print('erro adquirindo dados do readme', error)

        main_downloaded_stations = sorted(list(main_downloaded_stations), key=str.lower)
        return main_downloaded_stations, data_with_stations

    # ------------------------
    # Funções de exportação e info
    # ------------------------
    def inform_graph(self, selected_types, avarage_types):
        dialog = QDialog(self.root)
        dialog.setWindowTitle("Info Graph")
        dialog.resize(800, 400)

        layout = QVBoxLayout(dialog)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        inner = QWidget()
        inner_layout = QVBoxLayout(inner)

        text = ""
        for station in self.stations:
            text += f"\n\n{station}:\n"
            for t in selected_types:
                text += f"{t}: {avarage_types[station][t]}\n"
            text += "Hours got from Quite days:\n"
            if self.info_time:
                text += "\n".join(self.info_time[station])

        lbl = QLabel(text)
        lbl.setWordWrap(True)
        inner_layout.addWidget(lbl)
        scroll.setWidget(inner)
        layout.addWidget(scroll)
        dialog.exec_()

    def create_exporter_level_top(self, event, slct_types, is_difference=False):
        if event.button == 3:  # clique direito
            self.temp_window = QDialog(self.root)
            self.temp_window.setWindowTitle("Plot Downloader")
            self.temp_window.resize(250, 400)

            layout = QGridLayout(self.temp_window)
            self.checkboxes = {}
            row = 0
            for t in slct_types:
                cb = QCheckBox(t)
                layout.addWidget(cb, row, 0)
                self.checkboxes[t] = cb
                row += 1

            btn_confirm = QPushButton(self.util.dict_language[self.lang]['btn_confirm'])
            layout.addWidget(btn_confirm, row + 1, 0)
            btn_confirm.clicked.connect(lambda: self.export_file(is_difference))
            self.temp_window.exec_()

    def export_file(self, is_difference=False):
        save_file_path = QFileDialog.getExistingDirectory(self.root, "Select Directory")
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
                            lines += f'{self.all_data.get(station, {}).get(day, {}).get(time, {}).get(type, "None")}    '
                        lines += '\n'

                    date = day.split('/')
                    filepath = os.path.join(save_file_path,
                                            f'{station.lower()}{date[2]}{int(date[1]):02}{int(date[0]):02}.txt')
                    with open(filepath, 'w+') as file:
                        file.write(header + '\n' + lines)
        else:
            for day, times in self.diff_data.items():
                t = timedelta(hours=0, minutes=0)
                lines = ''
                for time in times:
                    hh = t.total_seconds() / 3600
                    lines += f'{hh:.2f}    '
                    t += timedelta(minutes=1)
                    for type in all_types:
                        lines += f'{self.diff_data.get(day, {}).get(time, {}).get(type, "None")}    '
                    lines += '\n'

                date = day.split('/')
                filepath = os.path.join(save_file_path,
                                        f'{self.min_station.lower()}-{self.sub_station.lower()}{date[2]}{int(date[1]):02}{int(date[0]):02}.txt')
                with open(filepath, 'w+') as file:
                    file.write(header + '\n' + lines)

        self.temp_window.accept()

    # ------------------------
    # Substituindo messageboxes nas funções auxiliares
    # ------------------------
    def _show_error(self, text):
        self.show_message(self.util.dict_language[self.lang]["mgbox_error"], text)
