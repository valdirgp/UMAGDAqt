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
    def createfile_readme(self, root, liststations_Embrace, liststations_Intermagnet, restart_page):
        # threading download preparation
        self.root = root
        total_downloads = len(liststations_Embrace) + len(liststations_Intermagnet)
        max_threads = 8
        self.semaphore_threading = mt.Semaphore(max_threads)
        self.info_embrace_stations = []
        self.info_intermagnet_stations = []

        self.request_embrace_queue = queue.Queue()
        self.request_intermagnet_queue = queue.Queue()
        for station in liststations_Embrace: self.request_embrace_queue.put(station.split()[0])
        for station in liststations_Intermagnet: self.request_intermagnet_queue.put(station.split()[0])

        self.threads = []
        for _ in range(int(max_threads/2)): 
            self.threads.append(mt.Thread(target=self.get_embrace_info))
            self.threads.append(mt.Thread(target=self.get_Intermagnet_info))

        # download start with threading
        self.create_progressbar('progbar_dwd_readme', total_downloads)
        for thread in self.threads: thread.start()
        self.check_write(restart_page)

    # searches station's full name in their files and location in embrace's readme
    def get_embrace_info(self):
        while not self.request_embrace_queue.empty():
            station = self.request_embrace_queue.get()
            station = 'VSS' if station == 'VSE' else station
            try:
                with self.semaphore_threading:
                    response = requests.get(f'https://embracedata.inpe.br/magnetometer/{station}/', verify=False)
                    soup = BeautifulSoup(response.content, 'html.parser')
                    links_year = soup.find_all('a')
                    for link_year in links_year:
                        year = link_year.get('href')
                        year = year.replace('/', '')
                            
                        if year.isdigit():
                            response = requests.get(f'https://embracedata.inpe.br/magnetometer/{station}/{year}/', verify=False)
                            soup = BeautifulSoup(response.content, 'html.parser')
                            linksday = soup.find_all('a')
                                
                            for linkday in linksday:
                                day = linkday.get('href')

                                if day[0].isalpha():
                                    response = requests.get(f'https://embracedata.inpe.br/magnetometer/{station}/{year}/{day}', verify=False)
                                    soup = BeautifulSoup(response.content, 'html.parser')
                                    text = soup.get_text()
                                    lines = text.split('\n')
                                    station_name = ''
                                        
                                    for i in lines[0]:
                                        if i != '-':
                                            station_name += i
                                        else:
                                            station_info = {'station_acronym': station, 'station_name': station_name.upper()} 
                                            break
                                    break
                            break

                    response = requests.get('https://embracedata.inpe.br/magnetometer/readme_magnetometer.txt', verify=False)
                    soup = BeautifulSoup(response.content, 'html.parser')
                    text = soup.get_text().split('\n')
                    for line in text: 
                        if re.search(station.lower(), line):
                            word = line.split()
                            station_info.update({'long': word[0], 'lat': word[1]})
                            self.info_embrace_stations.append(station_info)
                            break
            except Exception as error: 
                print('Erro no download readme(Embrace): ', error)
            finally:
                self.update_progressbar()

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
                self.update_progressbar()

    @staticmethod
    def resource_path(relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
            
        return os.path.join(base_path, relative_path)

    # writes readme file with obtained data from embrace and intermagnet
    def write_readme(self):
        with open(self.resource_path('readme_stations.txt'), 'w') as f:
            f.write("acronym     station                                             longitude     latitude    source\n")
            if self.info_embrace_stations: # check if embrace info was obtained
                for station in self.info_embrace_stations:
                    f.write(f"{station['station_acronym']: <10}  {station['station_name']: <50}  {station['long']: <12}  {station['lat']: <10}  EMBRACE\n")
            else:
                QMessageBox.information(
                    self.root,
                    self.util.dict_language[self.lang]["mgbox_error"],
                    self.util.dict_language[self.lang]["mgbox_error_readme_embrace"]
                )

            if self.info_intermagnet_stations: # check if intermagnet info was obtained
                for station in self.info_intermagnet_stations:
                    f.write(f"{station['station_acronym']: <10}  {station['station_name'].upper(): <50}  {station['long']: <12}  {station['lat']: <10}  INTERMAGNET\n")
            else:
                QMessageBox.information(
                    self.root,
                    self.util.dict_language[self.lang]["mgbox_error"],
                    self.util.dict_language[self.lang]["mgbox_error_readme_intermag"]
                )

    '''# checks if download is completed to write file and restart pages
    def check_write(self, restart_page):
        if self.porcentage < 100:
            # Em PyQt5, use QTimer.singleShot para agendar a checagem
            from PyQt5.QtCore import QTimer
            QTimer.singleShot(500, lambda: self.check_write(restart_page))
        else:
            self.write_readme()
            restart_page()'''
    
    def check_write(self, restart_page):
        if self.current_file < self.total_downloads:
            # Em PyQt5, use QTimer.singleShot para agendar a checagem
            from PyQt5.QtCore import QTimer
            QTimer.singleShot(500, lambda: self.check_write(restart_page))
        else:
            self.write_readme()
            restart_page()
