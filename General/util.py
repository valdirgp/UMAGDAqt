import os, sys
# Remover importação do ttk do tkinter
# from tkinter import ttk

from datetime import datetime
import numpy as np
from pyIGRF import igrf_value 

class Util():
    def __init__(self):
        self.dict_language = {"br": {
                                    "title": "UMAGDA - Univap Análise de dados de magnetômetros - FAPESP Project: 2022/14815-5 & 2024/05909-1",

                                    "menu_main": "Páginas",
                                    "menu_dwd": "Downloads",
                                    "menu_graph": "Gráficos",
                                    "menu_cd": "Gráficos Calmos e Perturbado",
                                    "menu_c": "Gráficos Calmos",
                                    "menu_config": "Configurações",
                                    "menu_lang": "Idioma",
                                    "menu_en":"Inglês",
                                    "menu_port":"Português",
                                    "menu_about": "Sobre",
                                    "menu_initial": "Início",
                                    "menu_lc": "Criar Licença",

                                    "lbl_st": "Estações",
                                    "lbl_dr": "Escolher Drive",
                                    "lbl_dur": "Duração",
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

                                    "progbar_dwd_Embrace": "Progresso Embrace",
                                    "progbar_dwd_Intermagnet": "Progresso Intermagnet",
                                    "progbar_dwd_readme": "Progresso Readme",

                                    "mgbox_error": "ERRO",
                                    "mgbox_error_st": "Selecione estação desejada",
                                    "mgbox_error_dur": "Digite a duração desejado",
                                    "mgbox_error_dur_type": "Digite tipo de duração desejada",
                                    "mgbox_error_dt_format": "formato de data inválido. Utilize DD/MM/YYYY.",
                                    "mgbox_error_dt_dif": "Data inválida. A data inicial deve ser menor do que a final",
                                    "mgbox_error_notfound": "Arquivo não foi encontrado",
                                    "mgbox_error_plt": "Erro ao gerar gráficos",
                                    "mgbox_error_noinfo": "Há uma falta de dados na data",
                                    "mgbox_error_nofound_embrace": "Não foi possível encontrar estações embrace",
                                    "mgbox_error_nofound_intermag": "Não foi possível encontrar estações intermagnet",
                                    "mgbox_error_notfound_st": "A Estação no perído especificado não foi encontrada em estações baixadas",
                                    "mgbox_error_info_ad": "Erro ao adquirir dados",
                                    "mgbox_error_inval_info": "Invalidez de dados para calcular na data",
                                    "mgbox_error_rowcol": "O número de colunas e linhas deve ser correspondente ao número de dias",
                                    "mgbox_error_reqlc": "Erro ao gerar pedido da licença",
                                    "mgbox_error_dt_type": "Selecione o tipo de dado desejado",
                                    "mgbox_error_noinfo_period":"Não há dados no período e estação referente",
                                    "mgbox_error_readme_embrace":"Não foi possível resgatar detalhes sobre embrace",
                                    "mgbox_error_readme_intermag":"Não foi possível resgatar detalhes sobre intermagnet",
                                    "mgbox_error_type":"Erro de tipo na estação",
                                    
                                    "mgbox_success": "Sucesso",
                                    "mgbox_success_reqlc": "Pedido de licença gerado com sucesso",

                                    "check_bold": "Negrito",
                                    "check_grid": "Grades",
                                    },
                            "en": {
                                    "title": "UMAGDA - Univap Magnetometer Data Analysis - FAPESP Project: 2022/14815-5 & 2024/05909-1",

                                    "menu_main": "Pages",
                                    "menu_dwd": "Downloads",
                                    "menu_graph": "Graphs",
                                    "menu_cd": "Calm and Disturb Graphs",
                                    "menu_c": "Calm Graphs",
                                    "menu_config": "Config",
                                    "menu_lang": "Language",
                                    "menu_en":"English",
                                    "menu_port":"Portuguese",
                                    "menu_about": "About",
                                    "menu_initial": "Initial",
                                    "menu_lc": "Create License",

                                    "lbl_st": "Stations",
                                    "lbl_dr": "Choose Drive",
                                    "lbl_dur": "Duration",
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

                                    "btn_slt": "Select All",
                                    "btn_clr": "Clear All",
                                    "btn_dwd": "Confirm Download",
                                    "btn_readme": "Create Readme File",
                                    "btn_confirm": "Confirm",

                                    "combo_day": "Day(s)",
                                    "combo_month": "Month(s)",
                                    "combo_year": "Year(s)",
                                    "combo_sing": "Single Day",
                                    "combo_sing_many": "Many Days",
                                    "combo_many": "Many Graphs",
                                    "combo_tide": "Tide",
                                    "combo_difference": "Difference",

                                    "progbar_dwd_Embrace": "Embrace Progress",
                                    "progbar_dwd_Intermagnet": "Intermagnet Progress",
                                    "progbar_dwd_readme": "Readme Pregress",

                                    "mgbox_error": "ERROR",
                                    "mgbox_error_st": "select a station",
                                    "mgbox_error_dur": "Enter a duration",
                                    "mgbox_error_dur_type": "Enter a duration type",
                                    "mgbox_error_dt_format": "Invalid date format. Use DD/MM/YYYY",
                                    "mgbox_error_dt_dif": "Invalid date. The start date must be less than the end date",
                                    "mgbox_error_notfound": "File was not found",
                                    "mgbox_error_plt": "Error creating graphs",
                                    "mgbox_error_noinfo": "There is a lack of data in the date",
                                    "mgbox_error_nofound_embrace": "Unable to find Embrace stations",
                                    "mgbox_error_nofound_intermag": "Unable to find Intermagnet stations",
                                    "mgbox_error_notfound_st": "Station in especified period was not found in downloaded stations",
                                    "mgbox_error_info_ad": "Error acquiring data",
                                    "mgbox_error_inval_info": "Invalidity of data to calculate on date",
                                    "mgbox_error_rowcol": "The number of columns and rows must correspond to the number of days",
                                    "mgbox_error_reqlc": "Error creating license request",
                                    "mgbox_error_dt_type": "Select the desired data type",
                                    "mgbox_error_noinfo_period":"There is no data for the corresponding period and station",
                                    "mgbox_error_readme_embrace":"Unable to retrieve details about embrace",
                                    "mgbox_error_readme_intermag":"Unable to retrieve details about intermagnet",
                                    "mgbox_error_type":"Type error in station",
                                    
                                    "mgbox_success": "Success",
                                    "mgbox_success_reqlc": "License request generated successfully",

                                    "check_bold": "Bold",
                                    "check_grid": "Grids",
                                    }
                            }
        
        self.dict_coord = {
                        "progbar_dwd_Embrace":"+500+300",
                        "progbar_dwd_Intermagnet":"+900+300",
                        "progbar_dwd_readme":"+500+300"
                        }

    # get the languge in config txt
    def get_language_config(self):
        with open(self.resource_path("config.txt"), "r") as f:
            file = f.read()
            data_list = file.split()
            return data_list[1]

    # change language config according to given lang <------- will have to be changed for future configs
    def change_lang(self, lang):
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

    # creates an absolute path
    @staticmethod
    def resource_path(relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath("./General")
            
        return os.path.join(base_path, relative_path)
    
    # destroy every existent frame in the window
    def destroy_existent_frames(self, root):
        # Em PyQt5, widgets filhos podem ser removidos assim:
        for widget in root.findChildren(type(root)):
            widget.setParent(None)

    # calcula o equador magnético baseado na longitude e latitude fornecida
    def calculate_inclination(self):
        self.ano = datetime.now().year
        dip = []
        #for long in range(-180, 181): 
        #     lat_range = np.linspace(-90, 90, 543)
        #     for lat in lat_range:
        #         result = igrf_value(lat, long, 0.0, self.ano)
        #         if abs(result[1]) <= 0.5:
        #             dip.append(lat)
        #             break
        
        for long in range(-180, 181):
            result = igrf_value(0.0, long, 0, self.ano)