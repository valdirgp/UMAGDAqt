from Model.DownloadPage.DownloadsModule import DownloadModule
from bs4 import BeautifulSoup
import requests
import os
from datetime import timedelta
import re
from charset_normalizer import detect
from urllib import request
import threading as mt
import queue
from PyQt5.QtWidgets import QMessageBox


class Intermagnet(DownloadModule):
    def __init__(self, language):
        super().__init__(language)

    # creates a list with all stations from the Intermagnet network
    def create_stationlist(self):
        try:
            response = requests.get(
                'https://imag-data.bgs.ac.uk/GIN_V1/GINForms2?observatoryIagaCode=AAE&publicationState=Best+available&dataStartDate=2024-06-09&dataDuration=1&submitValue=Bulk+Download+...&request=DataView&samplesPerDay=minute',
                timeout=15,
                verify=False)
            soup = BeautifulSoup(response.content, 'html.parser')
            options = soup.find_all('option')
            stations = []
            for option in options:
                station = option.get('value')
                if len(station) == 3 and station.isalpha():
                    station = 'VSI' if station.upper() == 'VSS' else station
                    stations.append(station.upper())
            return stations
        except Exception:
            QMessageBox.information(
                None,
                self.util.dict_language[self.lang]["mgbox_error"],
                "Erro ao conectar-se com intermagnet"
            )
            return []

    # gets information and control save data
    def initialize_download_Intermagnet(self, root, local_download, selected_stations, duration, duration_type, start_date):
        self.root = root
        self.lcl_download = local_download
        self.opener = request.build_opener(request.HTTPSHandler)

        number_days, final_date = self.calculate_num_days(int(duration), duration_type, start_date)
        total_downloads = number_days * len(selected_stations)

        max_threads = 8
        self.semaphore_threading = mt.Semaphore(max_threads)
        requests_list = []
        self.requests_queue = queue.Queue()

        for station in selected_stations:
            date = start_date
            while date != final_date:
                requests_list = self.add_request_queue(station, date, requests_list)
                date += timedelta(days=1)
        for req in requests_list:
            self.requests_queue.put(req)
        threads = []
        for _ in range(max_threads):
            threads.append(mt.Thread(target=self.get_file))

        self.create_progressbar("progbar_dwd_Intermagnet", total_downloads)
        for thread in threads:
            thread.start()

    def add_request_queue(self, station, date, requests_list):
        """makes queue for download with info from each request"""
        st = "VSS" if station == "VSI" else station
        url = (
            f"https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0"
            f"&observatoryIagaCode={st}&samplesPerDay=1440&orientation=Native&publicationState=adj-or-rep"
            f"&recordTermination=UNIX&dataStartDate={date.year}-{date.month:02}-{date.day:02}&dataDuration=1"
        )
        requests_list.append({"url": url, "station": station, "date": date})
        return requests_list

    # gets all the text
    def get_file(self):
        while not self.requests_queue.empty():
            request_info = self.requests_queue.get()
            try:
                with self.semaphore_threading:
                    with self.opener.open(request_info["url"]) as f_in:
                        raw_data = f_in.read()
                    result = detect(raw_data[:1000])
                    encoding = result["encoding"]
                    text = raw_data.decode(encoding)
                    lines = text.split("\n")

                    data_exists = False
                    for line in lines:
                        if re.search("Publication Date", line):
                            l = line.split()
                            if l[2] == "|":
                                print(
                                    f"Sem dados: {request_info['station'].lower()}"
                                    f"{request_info['date'].year}{request_info['date'].month:02}"
                                    f"{request_info['date'].day:02}min.min"
                                )
                            else:
                                data_exists = True
                            break

                    if data_exists:
                        directory_path = self.create_dict_path(
                            request_info["station"],
                            str(request_info["date"].year),
                            "INTERMAGNET"
                        )
                        file_path = os.path.join(
                            directory_path,
                            f"{request_info['station'].lower()}{str(request_info['date'].year)}"
                            f"{request_info['date'].month:02}{request_info['date'].day:02}min.min"
                        )
                        with open(file_path, "w+", encoding="utf-8") as file:
                            for line in lines:
                                file.write(line + "\n")
            except Exception as error:
                print(
                    f"Erro no download: {request_info['station'].lower()}"
                    f"{str(request_info['date'].year)}{request_info['date'].month:02}"
                    f"{request_info['date'].day:02}min.min: {error}"
                )
            finally:
                self.update_progressbar()
