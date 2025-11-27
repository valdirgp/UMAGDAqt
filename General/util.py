import os, sys
# Remover importação do ttk do tkinter
# from tkinter import ttk

from datetime import datetime
import numpy as np
from pyIGRF import igrf_value
import math

class Util():
    def __init__(self):
        self.dict_language = {"br": {
                                    "title": "UMAGDA - Univap Análise de dados de magnetômetros - FAPESP Project: 2022/14815-5 & 2024/05909-1",

                                    "menu_main": "Páginas",
                                    "menu_dwd": "Downloads",
                                    "menu_graph": "Gráficos",
                                    "menu_cd": "Gráficos Calmos e Perturbado",
                                    "menu_c": "Gráficos Calmos",
                                    "menu_ucd": "Gráficos Calmos e Pertubado Universal",
                                    "menu_config": "Configurações",
                                    "menu_lang": "Idioma",
                                    "menu_en":"Inglês",
                                    "menu_port":"Português",
                                    "menu_date": "Data",
                                    "menu_drive": "Drive",
                                    "menu_regiao": "Região",
                                    "mundo": "Mundo",
                                    "america_do_norte": "América do Norte",
                                    "america_do_sul": "América do Sul",
                                    "africa": "África",
                                    "europa": "Europa",
                                    "asia": "Ásia",
                                    "oceania": "Oceania",
                                    "menu_reset": "Reiniciar",
                                    "menu_about": "Sobre",
                                    "menu_initial": "Início",
                                    "menu_lc": "Criar Licença",

                                    "lbl_st": "Estações (lat, long, dip)",
                                    "lbl_dr": "Escolher Drive",
                                    "lbl_dur": "Duração",
                                    "lbl_C_options": "Opções de Plotagem",
                                    "lbl_dt": "Data",
                                    "lbl_init_dt": "Data de Início",
                                    "lbl_fin_dt": "Data Final",
                                    "lbl_plt": "Opções de Plotagem",
                                    "lbl_tpgraph": "Tipos de Gráficos",
                                    "lbl_calm": "Dias Calmos",
                                    "lbl_disturb": "Dias Perturbados",
                                    "lbl_noreadme": "Arquivo readme não está na pasta",
                                    "lbl_row": "Linhas",
                                    "lbl_colum": "Colunas",
                                    "lbl_lcr": "Criar Requisição de Licença",
                                    "lbl_name": "Nome",
                                    "lbl_inst": "Instituição",
                                    "lbl_dev": "Desenvolvido por",
                                    "lbl_contact": "Contato",
                                    "lbl_graph_opts": "Opções de Gráfico",
                                    "lbl_minuend": "Minuendo",
                                    "lbl_subtracted": "Subtraendo",
                                    "lbl_max_v": "Valor máximo",
                                    "lbl_min_v": "Valor mínimo",
                                    "lbl_no_data": "Sem Dados",
                                    "lbl_err_plot": "Erro ao plotar",
                                    "lbl_warn": "Lembrete",

                                    "btn_slt": "Selecionar Todos",
                                    "btn_clr": "Limpar Tudo",
                                    "btn_dwd": "Confirmar Download",
                                    "btn_readme": "Criar Arquivo Readme",
                                    "btn_confirm": "Confirmar",
                                    "btn_confirm_H": "Plotar valores de H(nT)",
                                    "btn_confirm_Z": "Plotar valores de Z(nT)",
                                    "btn_confirm_X": "Plotar valores de X",
                                    "btn_confirm_Y": "Plotar valores de Y",
                                    "btn_confirm_D": "Plotar valores de D",
                                    "btn_confirm_F": "Plotar valores de F",
                                    "btn_confirm_I": "Plotar valores de I",
                                    "btn_confirm_G": "Plotar valores de G",

                                    "btn_slt": "Selecionar Todos",
                                    "btn_clr": "Limpar Tudo",
                                    "btn_dwd": "Confirmar Download",
                                    "btn_readme": "Criar Arquivo Readme",
                                    "btn_confirm": "Confirmar",

                                    "combo_day": "Dia(s)",
                                    "combo_month": "Mês(es)",
                                    "combo_year": "Ano(s)",
                                    "combo_sing": "Um dia",
                                    "combo_sing_many": "Vários dias",
                                    "combo_many": "Vários Gráficos",
                                    "combo_tide": "Maré",
                                    "combo_difference": "Diferença",
                                    "combo_contorno": "Contorno",

                                    "progbar_dwd_Embrace": "Progresso Embrace",
                                    "progbar_dwd_Intermagnet": "Progresso Intermagnet",
                                    "progbar_dwd_readme": "Progresso Readme",

                                    "mgbox_error": "ERRO",
                                    "mgbox_error_st": "Selecione estação desejada",
                                    "mgbox_error_dur": "Digite a duração desejada",
                                    "mgbox_error_dur_type": "Digite tipo de duração desejada",
                                    "mgbox_error_calm_dates": "Selecione um dia calmo",
                                    "mgbox_error_disturb_dates": "Selecione um dia perturbado",
                                    "mgbox_error_dt_format": "formato de data inválido. Utilize DD/MM/YYYY.",
                                    "mgbox_error_dt_dif": "Data inválida. A data inicial deve ser menor do que a final",
                                    "mgbox_error_notfound": "Arquivo não foi encontrado",
                                    "mgbox_error_plt": "Erro ao gerar gráficos",
                                    "mgbox_error_plt_st": "É necessário inserir ao menos duas estações",
                                    "mgbox_error_noinfo": "Há uma falta de dados na data",
                                    "mgbox_error_nofound_embrace": "Não foi possível encontrar estações embrace",
                                    "mgbox_error_nofound_intermag": "Não foi possível encontrar estações intermagnet",
                                    "mgbox_error_notfound_st": "A Estação no perído especificado não foi encontrada em estações baixadas",
                                    "mgbox_error_info_ad": "Erro ao adquirir dados",
                                    "mgbox_error_inval_info": "Invalidez de dados para calcular na data",
                                    "mgbox_error_lincol": "Insira número de colunas e linhas",
                                    "mgbox_error_rowcol": "O número de colunas e linhas deve ser correspondente ao número de dias",
                                    "mgbox_error_reqlc": "Erro ao gerar pedido da licença",
                                    "mgbox_error_dt_type": "Selecione o tipo de dado desejado",
                                    "mgbox_error_noinfo_period":"Não há dados no período e estação referente",
                                    "mgbox_error_readme_embrace":"Não foi possível resgatar detalhes sobre embrace",
                                    "mgbox_error_readme_intermag":"Não foi possível resgatar detalhes sobre intermagnet",
                                    "mgbox_error_type":"Erro de tipo na estação",
                                    "mgbox_err_plot": "Não foi possivel criar o gráfico, não há dados",
                                    "mgbox_err_warn": "Por favor, escolha uma estação antes de plotar o gráfico.",
                                    
                                    "mgbox_success": "Sucesso",
                                    "mgbox_success_reqlc": "Pedido de licença gerado com sucesso",

                                    "check_bold": "Negrito",
                                    "check_grid": "Grades",

                                    "download_complete": "Download concluído:",
                                    "error_no_readable_data": "Erro no download (sem dados legíveis):",
                                    "error_download": "Erro no download:"
                                    },
                            "en": {
                                    "title": "UMAGDA - Univap Magnetometer Data Analysis - FAPESP Project: 2022/14815-5 & 2024/05909-1",

                                    "menu_main": "Pages",
                                    "menu_dwd": "Downloads",
                                    "menu_graph": "Graphs",
                                    "menu_cd": "Calm and Disturb Graphs",
                                    "menu_c": "Calm Graphs",
                                    "menu_ucd": "Universal Calm and Disturb Graphs",
                                    "menu_config": "Config",
                                    "menu_lang": "Language",
                                    "menu_en":"English",
                                    "menu_port":"Portuguese",
                                    "menu_date": "Date",
                                    "menu_drive": "Drive",
                                    "menu_regiao": "Region",
                                    "mundo": "World",
                                    "america_do_norte": "North America",
                                    "america_do_sul": "South America",
                                    "africa": "Africa",
                                    "europa": "Europe",
                                    "asia": "Asia",
                                    "oceania": "Oceania",
                                    "menu_reset": "Restart",
                                    "menu_about": "About",
                                    "menu_initial": "Initial",
                                    "menu_lc": "Create License",

                                    "lbl_st": "Stations (lat, long, dip)",
                                    "lbl_dr": "Choose Drive",
                                    "lbl_dur": "Duration",
                                    "lbl_C_options": "Plot Options",
                                    "lbl_dt": "Date",
                                    "lbl_init_dt": "Initial Date",
                                    "lbl_fin_dt": "Final Date",
                                    "lbl_plt": "Plot Options",
                                    "lbl_tpgraph": "Graphs Types",
                                    "lbl_calm": "Quite Days",
                                    "lbl_disturb": "Disturbed Days",
                                    "lbl_noreadme": "Readme is not in the folder",
                                    "lbl_row": "Rows",
                                    "lbl_colum": "Columns",
                                    "lbl_lcr": "Create License Request",
                                    "lbl_name": "Name",
                                    "lbl_inst": "Institution",
                                    "lbl_dev": "Developed by",
                                    "lbl_contact": "Contact",
                                    "lbl_graph_opts": "Graph Options",
                                    "lbl_minuend": "Minuend",
                                    "lbl_subtracted": "Subtracted",
                                    "lbl_max_v": "Maximum value",
                                    "lbl_min_v": "Minimum value",
                                    "lbl_no_data": "No Data",
                                    "lbl_err_plot": "Plot Error",
                                    "lbl_warn": "Reminder",

                                    "btn_slt": "Select All",
                                    "btn_clr": "Clear All",
                                    "btn_dwd": "Confirm Download",
                                    "btn_readme": "Create Readme File",
                                    "btn_confirm": "Confirm",

                                    "btn_confirm_H": "Plot H(nT) values",
                                    "btn_confirm_Z": "Plot Z(nT) values",
                                    "btn_confirm_X": "Plot X values",
                                    "btn_confirm_Y": "Plot Y values",
                                    "btn_confirm_D": "Plot D values",
                                    "btn_confirm_F": "Plot F values",
                                    "btn_confirm_I": "Plot I values",
                                    "btn_confirm_G": "Plot G values",

                                    "combo_day": "Day(s)",
                                    "combo_month": "Month(s)",
                                    "combo_year": "Year(s)",
                                    "combo_sing": "Single Day",
                                    "combo_sing_many": "Many Days",
                                    "combo_many": "Many Graphs",
                                    "combo_tide": "Tide",
                                    "combo_difference": "Difference",
                                    "combo_contorno": "Contour",

                                    "progbar_dwd_Embrace": "Embrace Progress",
                                    "progbar_dwd_Intermagnet": "Intermagnet Progress",
                                    "progbar_dwd_readme": "Readme Pregress",

                                    "mgbox_error": "ERROR",
                                    "mgbox_error_st": "select a station",
                                    "mgbox_error_dur": "Enter a duration",
                                    "mgbox_error_dur_type": "Enter a duration type",
                                    "mgbox_error_calm_dates": "Enter a calm day",
                                    "mgbox_error_disturb_dates": "Enter a disturbed day",
                                    "mgbox_error_dt_format": "Invalid date format. Use DD/MM/YYYY",
                                    "mgbox_error_dt_dif": "Invalid date. The start date must be less than the end date",
                                    "mgbox_error_notfound": "File was not found",
                                    "mgbox_error_plt": "Error creating graphs",
                                    "mgbox_error_plt_st": "It is necessary at least two stations",
                                    "mgbox_error_noinfo": "There is a lack of data in the date",
                                    "mgbox_error_nofound_embrace": "Unable to find Embrace stations",
                                    "mgbox_error_nofound_intermag": "Unable to find Intermagnet stations",
                                    "mgbox_error_notfound_st": "Station in especified period was not found in downloaded stations",
                                    "mgbox_error_info_ad": "Error acquiring data",
                                    "mgbox_error_inval_info": "Invalidity of data to calculate on date",
                                    "mgbox_error_lincol": "Enter number of columns and rows",
                                    "mgbox_error_rowcol": "The number of columns and rows must correspond to the number of days",
                                    "mgbox_error_reqlc": "Error creating license request",
                                    "mgbox_error_dt_type": "Select the desired data type",
                                    "mgbox_error_noinfo_period":"There is no data for the corresponding period and station",
                                    "mgbox_error_readme_embrace":"Unable to retrieve details about embrace",
                                    "mgbox_error_readme_intermag":"Unable to retrieve details about intermagnet",
                                    "mgbox_error_type":"Type error in station",
                                    "mgbox_err_plot": "Couldn't plot graph, no available data",
                                    "mgbox_err_warn": "Please select a station before plotting the graph.",
                                    
                                    "mgbox_success": "Success",
                                    "mgbox_success_reqlc": "License request generated successfully",

                                    "check_bold": "Bold",
                                    "check_grid": "Grids",

                                    "msgbox_info": "Information",
                                    "download_complete": "Download completed:",
                                    "error_no_readable_data": "Download error (data not readable):",
                                    "error_download": "Error during download:"
                                    }
                            }
        
        self.dict_coord = {
                        "progbar_dwd_Embrace":"+500+300",
                        "progbar_dwd_Intermagnet":"+900+300",
                        "progbar_dwd_readme":"+500+300"
                        }

    def createConfig(self):
        termos = ["lang:", "year:", "final:", "drive:", "regions{"]
        criar = False
        config_path = self.resource_path("config.txt")

        if os.path.isfile(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                conteudo = f.read().strip()

            if not conteudo:
                criar = True
            else:
                for termo in termos:
                    if termo not in conteudo:
                        criar = True
                        break
        else:
            criar = True

        if criar:
            from datetime import datetime
            import string

            ano_atual = datetime.now().year - 1
            mes_atual = datetime.now().month
            dia_atual = datetime.now().day
            yearEfinal = f"{dia_atual}/{mes_atual}/{ano_atual}"

            drives = [f"{d}:\\" for d in string.ascii_uppercase]
            drive = next((d for d in drives if os.path.exists(d)), None)

            regioes = '''
        "mundo":                      None;
        "america_do_norte":                      [-170, -30, 5, 85];
        "america_do_sul":                      [-82, -34, -56, 13];
        "africa":                      [-20, 55, -35, 37];
        "europa":                      [-25, 45, 34, 72];
        "asia":                      [25, 180, -10, 80];
        "oceania":                      [110, 180, -50, 10];'''

            with open(config_path, "w", encoding="utf-8") as f:
                config = ["en", yearEfinal, yearEfinal, drive, regioes]
                for termo, valor in zip(termos, config):
                    if termo != "regions{":
                        f.write(f"{termo} {valor}\n")
                    else:
                        f.write(termo + valor + "\n}\n")

                

    # get the languge in config txt
    def get_language_config(self):
        with open(self.resource_path("config.txt"), "r") as f:
            file = f.read()
            data_list = file.split()
            if "lang:" in data_list:
                idx = data_list.index("lang:")
                return data_list[idx + 1]
        return "en"

    # change language config according to given lang <------- will have to be changed for future configs
    def change_lang(self, lang):
        '''
        with open(self.resource_path("config.txt"), "r") as f:
            file = f.read()
            data_list = file.split()
            data_list[1] = lang

        with open(self.resource_path("config.txt"), "w") as f:
            for index, info in enumerate(data_list):
                if index % 2 == 0:
                    f.write(f"{info} ")
                else:
                    f.write(f"{info}\n")
        '''
        lines = []
        with open(self.resource_path("config.txt"), "r") as f:
            for line in f:
                if "regions{" not in line and '}' not in line:
                    if '"' not in line:
                        key, value = line.strip().split()
                    else:
                        key, value = line.strip().split(':')
                        key += ':'
                else:
                    key = line.strip()
                #key, value = line.strip().split()
                if key.strip() == "lang:":
                    lines.append(f"lang: {lang}\n")
                else:
                    lines.append(line)

        with open(self.resource_path("config.txt"), "w") as f:
            f.writelines(lines)
                    
    def get_year_config(self):
        with open(self.resource_path("config.txt"), "r") as f:
            file = f.read()
            data_list = file.split()
            if "year:" in data_list:
                idx = data_list.index("year:")
                data = data_list[idx + 1].split("/")
                for e, value in enumerate(data):
                    data[e] = int(value)
                return data
        from datetime import datetime

        ano_atual = datetime.now().year
        mes_atual = datetime.now().month
        dia_atual = datetime.now().day
        return [dia_atual, mes_atual, ano_atual]
    
    def change_year(self, year):
        lines = []
        with open(self.resource_path("config.txt"), "r") as f:
            for line in f:
                if "regions{" not in line and '}' not in line:
                    if '"' not in line:
                        key, value = line.strip().split()
                    else:
                        key, value = line.strip().split(':')
                        key += ':'
                else:
                    key = line.strip()
                #key, value = line.strip().split()
                if key.strip() == "year:":
                    lines.append(f"year: {year[0]}/{year[1]}/{year[2]}\n")
                else:
                    lines.append(line)

        with open(self.resource_path("config.txt"), "w") as f:
            f.writelines(lines)

    def get_final_config(self):
        with open(self.resource_path("config.txt"), "r") as f:
            file = f.read()
            data_list = file.split()
            if "final:" in data_list:
                idx = data_list.index("final:")
                data = data_list[idx + 1].split("/")
                for e, value in enumerate(data):
                    data[e] = int(value)
                return data
        from datetime import datetime

        ano_atual = datetime.now().year
        mes_atual = datetime.now().month
        dia_atual = datetime.now().day
        return [dia_atual, mes_atual, ano_atual]
    
    def change_final(self, final):
        lines = []
        with open(self.resource_path("config.txt"), "r") as f:
            for line in f:
                if "regions{" not in line and '}' not in line:
                    if '"' not in line:
                        key, value = line.strip().split()
                    else:
                        key, value = line.strip().split(':')
                        key += ':'
                else:
                    key = line.strip()
                #key, value = line.strip().split()
                if key.strip() == "final:":
                    lines.append(f"final: {final[0]}/{final[1]}/{final[2]}\n")
                else:
                    lines.append(line)

        with open(self.resource_path("config.txt"), "w") as f:
            f.writelines(lines)

    def get_drive_config(self):
        with open(self.resource_path("config.txt"), "r") as f:
            file = f.read()
            data_list = file.split()
            if "drive:" in data_list:
                idx = data_list.index("drive:")
                return data_list[idx + 1]
            
        if os.name == "nt":  # Windows
            # retorna o primeiro drive válido
            for d in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                path = f"{d}:\\"
                if os.path.exists(path):
                    return path
                else:  # Linux/macOS
                    return "/"  # normalmente sempre existe
                
    def change_drive(self, drive):
        lines = []
        with open(self.resource_path("config.txt"), "r") as f:
            for line in f:
                if "regions{" not in line and '}' not in line:
                    if '"' not in line:
                        key, value = line.strip().split()
                    else:
                        key, value = line.strip().split(':')
                        key += ':'
                else:
                    key = line.strip()
                #key, value = line.strip().split()
                if key.strip() == "drive:":
                    lines.append(f"drive: {drive}\n")
                else:
                    lines.append(line)

        with open(self.resource_path("config.txt"), "w") as f:
            f.writelines(lines)
    
    def insert_region(self, region, coordenadas):
        lines = []
        inserir= False
        with open(self.resource_path("config.txt"), "r") as f:
            for line in f:
                if "regions{" not in line and '}' not in line:
                    if '"' not in line:
                        key, value = line.strip().split()
                    else:
                        key, value = line.strip().split(':')
                        key += ':'
                else:
                    key = line.strip()
                if key == "regions{":
                    lines.append("regions{\n")
                    inserir = True
                elif inserir:
                    if key != "}":
                        lines.append(f"{key} {value}\n")
                    else:
                        lines.append(f'"{region}": {coordenadas};')
                        inserir = False
                else:
                    lines.append(line)
        with open(self.resource_path("config.txt"), "w") as f:
            lines.append("\n}")
            f.writelines(lines)
    
    def get_region(self):
        with open(self.resource_path("config.txt"), "r") as f:
            file = f.read()
            if "regions{" in file:
                data_list = file.replace("}", "")
                data_list = data_list.replace("\n", "")
                data_list = data_list.split("{")
                key_value = data_list[1].split(";")
                key_value.pop()
                data = []
                for item in key_value:
                    item = item.split(":")
                    item[0] = item[0].replace('"', '')
                    item[0] = item[0].strip('\n')
                    item[0] = item[0].strip()
                    item[1] = item[1].strip()
                    item[1] = item[1].strip('[')
                    item[1] = item[1].strip(']')
                    item[1] = item[1].split(',')
                    data.append(item)
            return data
    

    # creates an absolute path
    @staticmethod
    def resource_path(relative_path):
        try:
            base_path = sys._MEIPASS
            base_path = os.path.join(base_path, "")
        except Exception:
            base_path = os.path.abspath(".")
            
        #return os.path.join(base_path, relative_path)
        return(relative_path)
    
    @staticmethod
    def resource_pathGeneral(relative_path):
        try:
            base_path = sys._MEIPASS
            base_path = os.path.join(base_path, "General")
        except Exception:
            base_path = os.path.abspath("./General")
            
        return os.path.join(base_path, relative_path)
    
    def destroy_existent_frames(self, root):
        for widget in root.findChildren(type(root)):
            widget.setParent(None)

    def to_decimal_year(self, dt_object: datetime) -> float:
        year_start = datetime(dt_object.year, 1, 1)
        year_end = datetime(dt_object.year + 1, 1, 1)

        days_in_year = (year_end - year_start).days

        day_of_year = (dt_object - year_start).days

        return dt_object.year + (day_of_year / days_in_year)

    # calcula o equador magnético baseado na longitude e latitude fornecida
    def calculate_inclination(self, ano):
        ano = datetime(ano[2], ano[1], ano[0])
        self.ano = self.to_decimal_year(ano)
        dip = []
        for long in range(-180, 181):
            result = igrf_value(0.0, long, 300, self.ano) 
            dip.append(-math.degrees(math.atan((math.tan(math.radians(result[1]))/2))))  # Inclinação magnética 
        return dip