from Model.DownloadPage.DownloadsModule import DownloadModule
import requests
import os
from datetime import timedelta
from charset_normalizer import detect
import threading as mt
import queue
from PyQt5.QtWidgets import QMessageBox
from General.util import Util
import math
from pyIGRF import igrf_value
from datetime import datetime

class Embrace(DownloadModule):
    def __init__(self, language, root=None):
        super().__init__(language, root)
        self.util = Util()
    # creates a list with all stations from the Embrace network

    def obter_coordenadas_estacoes_embrace(self):
        """
        Lê todas as estações EMBRACE a partir do arquivo readme_stations.txt ou do readme oficial.
        """
        estacoes = {}
        # Tenta ler o arquivo local primeiro
        if os.path.exists(self.util.resource_path('readme_stations.txt')):
            try:
                with open(self.util.resource_path('readme_stations.txt'), 'r') as f:
                    for line in f:
                        if line.strip().endswith('EMBRACE'):
                            parts = line.split()
                            codigo = parts[0].upper()
                            try:
                                longitude = float(parts[-3])
                                latitude = float(parts[-2])
                                codigo = 'VSE' if codigo == 'VSS' else codigo
                                estacoes[codigo] = {'latitude': latitude, 'longitude': longitude}
                            except (ValueError, IndexError):
                                continue
                if estacoes:
                    return estacoes
            except Exception as e:
                print(f"Erro ao ler readme_stations.txt: {e}")

        # Se o arquivo local não existir ou falhar, busca da URL
        url = 'https://embracedata.inpe.br/magnetometer/readme_magnetometer.txt'
        try:
            with requests.get(url, timeout=15, verify=False) as response:
                text = response.text
                for line in text.splitlines():
                    if not line.strip() or line.startswith('#') or line.startswith('For'):
                        continue
                    parts = line.split()
                    if len(parts) < 3:
                        continue
                    try:
                        longitude = float(parts[0].replace(',', '.'))
                        latitude = float(parts[1].replace(',', '.'))
                        codigo = parts[2].upper()
                        codigo = 'VSE' if codigo == 'VSS' else codigo
                        estacoes[codigo] = {'latitude': latitude, 'longitude': longitude}
                    except ValueError:
                        continue
            return estacoes
        except Exception as e:
            print(f"Erro ao obter estações EMBRACE da URL: {e}")
            return {}
        
    def to_decimal_year(self, dt_object: datetime) -> float:
        """
        Converts a datetime object to a decimal year.
        
        This function correctly accounts for leap years.
        
        Args:
            dt_object (datetime): The datetime object to convert.
        
        Returns:
            float: The date and time as a decimal year.
        """

        year_start = datetime(dt_object.year, 1, 1)
        year_end = datetime(dt_object.year + 1, 1, 1)

        days_in_year = (year_end - year_start).days

        day_of_year = (dt_object - year_start).days

        return dt_object.year + (day_of_year / days_in_year)

    def create_stationlist(self, ano):
        ano = datetime(ano[2], ano[1], ano[0])
        self.ano = self.to_decimal_year(ano)
        stations = []
        codigos = []
        try:
            estacoes = self.obter_coordenadas_estacoes_embrace()
            for codigo, coords in estacoes.items():
                result = igrf_value(coords['latitude'], coords['longitude'], 0.300, self.ano)
                dip = -math.degrees(math.atan((math.tan(math.radians(result[1]))/2)))
                stations.append(f'{codigo} ({coords["latitude"]:.5f}, {coords["longitude"]:.5f}, {dip:.5f})')
                codigos.append(codigo)
            return stations, codigos
        except Exception as e:
            QMessageBox.information(
                self.root,
                self.util.dict_language[self.lang]["mgbox_error"],
                f'Erro ao conectar-se com EMBRACE: {e}'
            )
            return [], []

    
    # gets information and control save data
    def initialize_download_Embrace(self, root, local_download, selected_stations, duration, duration_type, start_date):
        self.root = root
        self.lcl_download = local_download
        #self.opener = request.build_opener(request.HTTPSHandler)
        import ssl
        from urllib import request

        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        self.opener = request.build_opener(request.HTTPSHandler(context=ctx))

        number_days, final_date = self.calculate_num_days(int(duration), duration_type, start_date)
        total_downloads = number_days * len(selected_stations)

        # threading download preparation
        max_threads = 8
        self.semaphore_threading = mt.Semaphore(max_threads)
        self.request_queue = queue.Queue()
        requests_list = []
        for station in selected_stations:
            date = start_date
            while date != final_date:
                requests_list = self.add_request_queue(station, date, requests_list)
                date += timedelta(days=1)
        for req in requests_list:
            self.request_queue.put(req)
        threads = []
        for _ in range(max_threads):
            threads.append(mt.Thread(target=self.get_file))
        self.responses.clear()
        
        # download start with threading
        self.create_progressbar('progbar_dwd_Embrace', total_downloads)
        for thread in threads:
            thread.start()

    # makes queque for download with info from each request
    def add_request_queue(self, station, dt, requests):
        monthchar = self.format_month(dt.month)
        st = 'VSS' if station == 'VSE' else station
        url = f'https://embracedata.inpe.br/magnetometer/{st}/{dt.year}/{st.lower()}{dt.day:02}{monthchar}.{str(dt.year)[2:]}m'
        requests.append({'url': url, 'station': station, 'date': dt})
        return requests

    # gets all the text from the embrace file
    responses = []
    responses.append("Embrace")
    def get_file(self):
        while not self.request_queue.empty():
            request_item = self.request_queue.get()
            try:
                with self.semaphore_threading:
                    # gets info from web and decode it 
                    with self.opener.open(request_item['url'], timeout=20) as file: 
                        raw_data = file.read()
                    result = detect(raw_data[:1000])
                    encoding = result['encoding']
                    text = raw_data.decode(encoding)
                    lines = text.split('\n')
                    
                    # verifies if archive has valid data 
                    if self.is_string_readable_by_line(lines) and len(lines) > 1:
                        time_delta = timedelta(hours=0, minutes=0)
                        self.hours_counted = set()
                        can_count = False
                        count = 0
                        while True:
                            try:
                                if can_count:
                                    total_seconds = time_delta.total_seconds()
                                    hh = int(total_seconds // 3600)
                                    mm = int((total_seconds % 3600) // 60)

                                    line = lines[count].split()
                                    if line == '': lines.pop(count)

                                    if len(line) == 10:
                                        if f'{hh:02}' != line[3]:# sees if the h exists in the archive comparing with own counter
                                            if f'{hh-1:02}' == line[3] and f'{mm:02}' == line[4]:# sees if there is a clean space between h and min
                                                lines.pop(count)
                                                self.insert_clean_data(lines, count, request_item['date'], hh, mm)
                                            elif f'{line[3]}:{line[4]}' in self.hours_counted:# sees if there is a repeated hour/min
                                                lines.pop(count)
                                                continue
                                            else:
                                                self.insert_clean_data(lines, count, request_item['date'], hh, mm)

                                        elif f'{mm:02}' != line[4]:# sees if the minute exists in the archive comparing with own counter
                                            if f'{hh-1:02}' == line[3] and f'{mm:02}' == line[4]:# sees if there is a clean space between h and min
                                                lines.pop(count)
                                                self.insert_clean_data(lines, count, request_item['date'], hh, mm)
                                            elif f'{line[3]}:{line[4]}' in self.hours_counted:# sees if there is a repeated hour/min
                                                lines.pop(count)
                                                continue
                                            else:
                                                self.insert_clean_data(lines, count, request_item['date'], hh, mm)

                                        elif f'{hh:02}' == line[3] and f'{mm:02}' == line[4]:
                                            self.hours_counted.add(f'{line[3]}:{line[4]}')

                                    elif (len(line) > 0 and len(line) < 10) or len(line) > 10:# sees if all data in the hour is there
                                        lines.pop(count)
                                        self.insert_clean_data(lines, count, request_item['date'], hh, mm)
                                    elif len(line) == 0:
                                        self.insert_clean_data(lines, count, request_item['date'], hh, mm)
                                    
                                    if hh == 23 and mm == 59:
                                        break
                                    time_delta += timedelta(minutes=1)
                                    
                                else:
                                    if count == 3: can_count = True

                                lines[count] = lines[count].replace('\r','').replace('\n','')
                                count+=1

                            except IndexError:
                                self.insert_clean_data(lines, count, request_item['date'], hh, mm)
                        
                        # file creation
                        directory_path = self.create_dict_path(request_item['station'], str(request_item['date'].year), 'EMBRACE')
                        file_path = os.path.join(directory_path, f'{request_item["station"].lower()}{str(request_item["date"].year)}{request_item["date"].month:02}{request_item["date"].day:02}min.min')
                        with open(file_path, 'w+', encoding='utf-8') as file:
                            for _, line  in enumerate(lines):
                                file.write(line+'\n')
                        print(f'{self.util.dict_language[self.lang]["download_complete"]} {request_item["station"].lower()}{str(request_item["date"].year)}{request_item["date"].month:02}{request_item["date"].day:02}min.min')
                        self.responses.append(f"{self.util.dict_language[self.lang]["download_complete"]} {request_item['station'].lower()}{request_item['date'].year}{request_item['date'].month:02}{request_item['date'].day:02}min.min")
                        self.progress_signal.emit(
                            f"{self.util.dict_language[self.lang]["download_complete"]} {request_item['station'].lower()}{request_item['date'].year}{request_item['date'].month:02}{request_item['date'].day:02}min.min",
                            self.responses
                        )
                    else:
                        print(f'{self.util.dict_language[self.lang]["error_no_readable_data"]} {request_item["station"].lower()}{str(request_item["date"].year)}{request_item["date"].month:02}{request_item["date"].day:02}min.min')
                        self.responses.append(f"{self.util.dict_language[self.lang]["error_no_readable_data"]} {request_item['station'].lower()}{request_item['date'].year}{request_item['date'].month:02}{request_item['date'].day:02}min.min")
                        self.progress_signal.emit(
                            f"{self.util.dict_language[self.lang]["error_no_readable_data"]} {request_item['station'].lower()}{request_item['date'].year}{request_item['date'].month:02}{request_item['date'].day:02}min.min",
                            self.responses
                        )
            except Exception as error:
                print(f'{self.util.dict_language[self.lang]["error_download"]} {request_item["station"].lower()}{str(request_item["date"].year)}{request_item["date"].month:02}{request_item["date"].day:02}min.min: {error}')
                self.responses.append(f"{self.util.dict_language[self.lang]["error_download"]} {request_item['station'].lower()}{request_item['date'].year}{request_item['date'].month:02}{request_item['date'].day:02}min.min ({error})")
                self.progress_signal.emit(
                    f"{self.util.dict_language[self.lang]["error_download"]} {request_item['station'].lower()}{request_item['date'].year}{request_item['date'].month:02}{request_item['date'].day:02}min.min ({error})",
                    self.responses
                )
            '''finally:
                #self.update_progressbar()

                self.progress_signal.emit()   # <-- em vez de self.update_progressbar()'''
        self.responses.clear()

    # insert a clean data into the list
    def insert_clean_data(self, text, counter, date, hh, mm):
        text.insert(
            counter, 
            f' {date.day:02} {date.month:02} {date.year}  {hh:02} {mm:02}  99999.00 99999.00 99999.00 99999.00 99999.00'
            )
        self.hours_counted.add(f'{hh:02}:{mm:02}')