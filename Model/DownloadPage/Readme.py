from Model.DownloadPage.DownloadsModule import DownloadModule
from General.util import Util
import threading as mt
import queue
from bs4 import BeautifulSoup
import requests
from urllib import request
from urllib.error import URLError
import re
from charset_normalizer import detect
from urllib3.exceptions import InsecureRequestWarning
from PyQt5.QtWidgets import QMessageBox
import sys, os

class Readme(DownloadModule):
    def __init__(self, language, root=None):
        super().__init__(language, root)
        self.util = Util()
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    # create readme file with all stations and their acronym
    def createfile_readme(self, root, liststations_Embrace, liststations_Intermagnet, liststations_Lisn, restart_page):
        # threading download preparation
        self.root = root
        total_downloads = len(liststations_Embrace) + len(liststations_Intermagnet) + len(liststations_Lisn)
        max_threads = 8
        self.semaphore_threading = mt.Semaphore(max_threads)
        self.info_embrace_stations = []
        self.info_intermagnet_stations = []
        self.info_lisn_stations = []

        self.request_embrace_queue = queue.Queue()
        self.request_intermagnet_queue = queue.Queue()
        self.request_lisn_queue = queue.Queue()
        for station in liststations_Embrace: self.request_embrace_queue.put(station.split()[0])
        for station in liststations_Intermagnet: self.request_intermagnet_queue.put(station.split()[0])
        for station in liststations_Lisn: self.request_lisn_queue.put(station.split()[0])


        self.threads = []
        for _ in range(int(max_threads/2)): 
            self.threads.append(mt.Thread(target=self.get_embrace_info))
            self.threads.append(mt.Thread(target=self.get_Intermagnet_info))
            self.threads.append(mt.Thread(target=self.get_Lisn_info))

        # download start with threading
        self.create_progressbar('progbar_dwd_readme', total_downloads)
        for thread in self.threads: thread.start()
        self.check_write(restart_page)

    # searches station's full name and location in EMBRACE readme
    def get_embrace_info(self):
        while not self.request_embrace_queue.empty():

            station = self.request_embrace_queue.get()
            station = 'VSS' if station == 'VSE' else station

            try:
                with self.semaphore_threading:

                    station_info = {
                        'station_acronym': station,
                        'station_name': station
                    }


                    url = (
                        'https://embracedata.inpe.br/magnetometer/readme_magnetometer.html'
                    )

                    response = requests.get(
                        url,
                        verify=False,
                        timeout=15
                    )

                    text = response.text

                    for line in text.splitlines():

                        if "|" not in line:
                            continue

                        parts = line.split("|")

                        if len(parts) < 4:
                            continue

                        try:
                            longitude = float(parts[1].strip())
                            latitude = float(parts[2].strip())

                            station_part = parts[3].strip()

                            codigo = station_part.split()[0].upper()

                            codigo = "VSE" if codigo == "VSS" else codigo

                            if codigo != station.upper():
                                continue

                            station_info["station_acronym"] = station.strip()
                            station_info["station_name"] = station_part.split("-", 1)[1].strip()
                            station_info["long"] = longitude
                            station_info["lat"] = latitude

                            self.info_embrace_stations.append(
                                station_info
                            )

                            break

                        except ValueError:
                            continue


                        '''# procura a estação pelo código
                        if station.upper() not in [
                            x.upper() for x in cols
                        ]:
                            continue


                        try:

                            # procura latitude e longitude
                            for i, value in enumerate(cols):

                                if "longitude" in value.lower():

                                    station_info["long"] = float(
                                        cols[i+1]
                                        .replace(",", ".")
                                    )


                                if "latitude" in value.lower():

                                    station_info["lat"] = float(
                                        cols[i+1]
                                        .replace(",", ".")
                                    )


                            station_info["station_name"] = (
                                cols[1]
                                if len(cols) > 1
                                else station
                            )


                        except Exception:
                            pass


                        break'''


            except Exception as error:

                print(
                    "Erro no download readme(Embrace): ",
                    error
                )


            finally:
                #self.update_progressbar()
                self.progress_signal.emit("", [])

    # searches intermagnet info in its files
    def get_Intermagnet_info(self):
        while not self.request_intermagnet_queue.empty():
            station = self.request_intermagnet_queue.get()
            station = 'VSS' if station == 'VSI' else station
            try:
                with self.semaphore_threading:
                    url = f'https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode={station}&samplesPerDay=1440&orientation=Native&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=1900-01-01&dataDuration=1'
                    default_handler = request.HTTPSHandler
                    opener = request.build_opener(default_handler)
                    station_info = {}
                    try:
                        with opener.open(url) as f_in: raw_data = f_in.read()
                        result = detect(raw_data[:1000])
                        encoding = result['encoding']
                        text = raw_data.decode(encoding)
                        lines = text.split('\n')

                        for line in lines:
                            l = re.split(r'\s{2,}', line)
                            if re.search('^ Station Name', line):
                                station_info['station_name'] = l[1].replace('|', '')
                                station_info['station_acronym'] = station
                            elif re.search('^ Geodetic Latitude', line):
                                station_info['lat'] = l[1]
                            elif re.search('^ Geodetic Longitude', line):    
                                station_info['long'] = l[1]
                            
                    except (URLError, IOError, OSError) as error:
                        print(f'Erro no download readme {station}', error)
            
                    self.info_intermagnet_stations.append(station_info)
            except Exception as error:
                print(f'Erro no download readme(Intermagnet): ', error)
            finally:
                #self.update_progressbar()
                self.progress_signal.emit("", [])

    def get_Lisn_info(self):
        url = 'https://raw.githubusercontent.com/Thiago-Mancilla/LISN_STATIONS/main/readme_magnetometer.txt'
        try:
            response = requests.get(url, verify=False, timeout=15)
            lines_file = response.text.splitlines()
        except Exception as error:
            print(f'Erro no download readme(LISN): {error}')
            lines_file = []
        
        while not self.request_lisn_queue.empty():
            station = self.request_lisn_queue.get()
            try:
                with self.semaphore_threading:
                    for line in lines_file:
                        if not line.strip() or line.startswith('#'): continue
                        parts = line.split()
                        if len(parts) < 5: continue
                        
                        if parts[0].upper() == station.upper():
                            # parts structure: [CODE, Name..., Long, Lat, Source]
                            self.info_lisn_stations.append({'station_acronym': parts[0].upper(), 'long': parts[-3], 'lat': parts[-2], 'station_name': ' '.join(parts[1:-3])})
                            break
            except Exception as error:
                print(f'Erro ao processar estação LISN {station}: {error}')
            finally:
                #self.update_progressbar()
                self.progress_signal.emit("", [])

    # writes readme file with obtained data from embrace and intermagnet
    def write_readme(self):

        # normaliza os nomes antes de calcular o tamanho
        all_stations = (
            self.info_embrace_stations +
            self.info_intermagnet_stations +
            self.info_lisn_stations
        )

        headers = [
            "acronym",
            "station",
            "longitude",
            "latitude",
            "source"
        ]

        widths = [
            max(len(headers[0]), max(len(s['station_acronym']) for s in all_stations)) + 4,
            max(len(headers[1]), max(len(s['station_name']) for s in all_stations)) + 4,
            len(headers[2]) + 4,
            len(headers[3]) + 4,
            len(headers[4]) + 4
        ]


        def format_station(station):

            longitude = float(station['long'])

            if longitude > 180:
                longitude -= 360

            values = [
                station['station_acronym'].strip(),
                station['station_name'].strip().upper(),
                f"{longitude:.5f}",
                f"{float(station['lat']):.5f}",
                station['source'].strip()
            ]

            return "".join(
                value.ljust(width)
                for value, width in zip(values, widths)
            ) + "\n"


        with open(self.util.resource_path('readme_stations.txt'), 'w') as f:

            f.write(
                "".join(
                    h.ljust(w)
                    for h, w in zip(headers, widths)
                )
                + "\n"
            )

            if self.info_embrace_stations: # check if embrace info was obtained
                for station in self.info_embrace_stations:
                    station['source'] = "EMBRACE"
                    f.write(format_station(station))
            else:
                QMessageBox.information(
                    self.root,
                    self.util.dict_language[self.lang]["mgbox_error"],
                    self.util.dict_language[self.lang]["mgbox_error_readme_embrace"]
                )

            if self.info_intermagnet_stations: # check if intermagnet info was obtained
                for station in self.info_intermagnet_stations:
                    station['source'] = "INTERMAGNET"
                    f.write(format_station(station))
            else:
                QMessageBox.information(
                    self.root,
                    self.util.dict_language[self.lang]["mgbox_error"],
                    self.util.dict_language[self.lang]["mgbox_error_readme_intermag"]
                )
            
            if self.info_lisn_stations:
                for station in self.info_lisn_stations:
                    station['source'] = "LISN"
                    f.write(format_station(station))
            else:
                QMessageBox.information(
                    self.root,
                    self.util.dict_language[self.lang]["mgbox_error"],
                    self.util.dict_language[self.lang]["mgbox_error_readme_lisn"]
                )

    def check_write(self, restart_page):
        if self.current_file < self.total_downloads:
            from PyQt5.QtCore import QTimer
            QTimer.singleShot(500, lambda: self.check_write(restart_page))
        else:
            self.write_readme()
            restart_page()
    
    '''def restart_page(self):
        if self.root:
            self.root.config_page()'''
