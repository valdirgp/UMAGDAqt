import os
import shutil
import cartopy.crs as ccrs
from Model.GraphPage.GraphsModule import GraphsModule
from Model.Custom.CustomPltOptions import CustomPltOptions
from General.util import Util
from datetime import datetime, timedelta
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QDate, Qt
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from scipy.interpolate import griddata, Rbf, NearestNDInterpolator
from scipy.spatial import Delaunay
from matplotlib.colors import Normalize
from matplotlib.path import Path

from PyQt5.QtWidgets import QMessageBox, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton


class ContourGraph(GraphsModule):
    def __init__(self, root, language):
        self.root = root
        self.lang = language
        self.util = Util()
        super().__init__(self.lang)

    def plot_contour(self, local_downloaded, stations, selected_types, bold_text, grid_graph,

                            start, end, selected_dates, data_with_stations, contornoMap, map_widget):
            """
            Gera gráfico de contorno a partir de múltiplas estações.

            O eixo Y representa as estações (em suas latitudes).

            O eixo X representa o tempo.

            A intensidade é o valor interpolado entre as estações.

            """
    
            self.lcl_downloaded = local_downloaded

            self.stations = stations

            self.bold_text = bold_text

            self.grid_graph = grid_graph

            self.slct_dates = selected_dates

            self.data_with_stations = data_with_stations

            self.slct_types = selected_types

    

            self._original_clim = None   

            # --- Original functionality ---


                

            self.start_date, self.end_date = self.format_dates(start, end)

            self.end_date += timedelta(days=1)

            if not self.start_date:

                return

            self.all_data = self.get_stations_data()

            if not self.all_data:

                return

            self.can_plot = True

            for slct_type in selected_types:
                if 'd' in slct_type:

                    self.add_delta_dict(slct_type)

            if 'reference' in selected_types:

                selected_types.remove('reference')

                selected_types.extend(f'{type.replace("d", "")}-reference' for type in selected_types if 'd' in type)

                self.add_reference(selected_types)

            avarage_types = self.calculate_type_averages(selected_types, stations)

            if not avarage_types:

                return
            if contornoMap != None:

                self.regiao = contornoMap[0]

                self.title = str(contornoMap[1])
                # Correção: Converter os valores de escala para float.
                self.min_scale = float(contornoMap[2])

                self.max_scale = float(contornoMap[3])

                self.ticks = int(contornoMap[4])

                self.start_time = str(contornoMap[5])

                self.end_time = str(contornoMap[6])

                self.interval = str(contornoMap[7])

                self.save_contour_map_sequence(map_widget, selected_types[0])
                # Correção: Remover o 'return' para permitir que o gráfico geral também seja plotado.

            self.add_plots(selected_types)

            self.config_graph(selected_types)

            if not self.can_plot:

                return

            plt.show()

            year_config = self.util.get_year_config()

            final_config = self.util.get_final_config()
            
            if self.start_date.day != year_config[0] or self.start_date.month != year_config[1] or self.start_date.year != year_config[2]:

                self.util.change_year([self.start_date.day, self.start_date.month, self.start_date.year])

            if (self.end_date - timedelta(days=1)).day != final_config[0] or (self.end_date - timedelta(days=1)).month != final_config[1] or (self.end_date - timedelta(days=1)).year != final_config[2]:

                self.util.change_final([(self.end_date - timedelta(days=1)).day, (self.end_date - timedelta(days=1)).month, (self.end_date - timedelta(days=1)).year])
        

    def save_contour_map_sequence(self, map_widget, plot_type):
        from matplotlib.colors import LinearSegmentedColormap
        import cartopy.feature as cfeature
        import matplotlib.pyplot as plt
        
        # Diretório de saída
        output_dir = f"Contour_Maps/{self.title}"
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
        os.makedirs(output_dir, exist_ok=True)

        images_saved_count = 0

        # Cores para o colormap
        cores = [
            (0, 0, 0.5),      # azul escuro
            (0, 0.5, 1),     # azul claro
            (1, 1, 0),       # amarelo
            (1, 0.5, 0),     # laranja
            (1, 0, 0)       # vermelho
        ]
        cmap_custom = LinearSegmentedColormap.from_list("custom_cmap", cores)

        # Parsing dos tempos
        start_t = datetime.strptime(self.start_time, "%H:%M").time()
        end_t = datetime.strptime(self.end_time, "%H:%M").time()
        interval_parts = [int(p) for p in self.interval.split(':')]
        interval_delta = timedelta(hours=interval_parts[0], minutes=interval_parts[1])

        current_date_iterator = self.start_date
        end_date_exclusive = self.end_date

        while current_date_iterator < end_date_exclusive:
            day_start_dt = datetime.combine(current_date_iterator, start_t)

            if end_t < start_t:
                day_end_dt = datetime.combine(current_date_iterator + timedelta(days=1), end_t)
            else:
                day_end_dt = datetime.combine(current_date_iterator, end_t)

            current_time_dt = day_start_dt
            while current_time_dt <= day_end_dt:

                # Correção: Usar formato sem zero à esquerda para dia/mês para corresponder às chaves de dados
                day_str_lookup = f"{current_time_dt.day}/{current_time_dt.month}/{current_time_dt.year}" 
                time_str_lookup = f"{current_time_dt.hour}:{current_time_dt.minute}"

                lons, lats, vals, active_stations = [], [], [], []
                # Correção: Iterar apenas sobre as estações selecionadas pelo usuário.
                for station_full_name in self.stations:
                    station_code = station_full_name.split()[0]
                    station_data = self.all_data.get(station_code, {})
                    if day_str_lookup in station_data:
                        time_data = station_data[day_str_lookup].get(time_str_lookup)
                        
                        if time_data and time_data.get(plot_type) is not None:
                            info = self.data_with_stations.get(station_code)
                            # Correção: Encontra o dicionário completo da estação, comparando apenas o código.
                            station_info_full = next((s for s in map_widget.all_locals if s['station'].split()[0] == station_code), None)
                            if info and station_info_full and time_data.get(plot_type) is not None and not np.isnan(time_data[plot_type]):
                                # Correção: Usar as coordenadas geográficas do widget do mapa para consistência.
                                lons.append(station_info_full['longitude'])
                                lats.append(station_info_full['latitude'])
                                vals.append(time_data[plot_type])
                                active_stations.append(station_info_full)

                if not lons:
                    current_time_dt += interval_delta
                    continue
                
                # Cria uma nova figura e eixos em memória para cada imagem
                fig = plt.figure(figsize=(10, 8))
                ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

                # Adiciona as features do mapa (terra, oceano, etc.) ANTES de plotar os dados
                ax.add_feature(cfeature.LAND)
                ax.add_feature(cfeature.OCEAN)
                ax.add_feature(cfeature.COASTLINE)
                ax.add_feature(cfeature.BORDERS)
                
                ax.set_extent(self.regiao, crs=ccrs.PlateCarree())

                # Redesenha as estações no mapa temporário
                ax.scatter([s['longitude'] for s in map_widget.all_locals if s['station'].split()[0] in [st.split()[0] for st in self.stations]], [s['latitude'] for s in map_widget.all_locals if s['station'].split()[0] in [st.split()[0] for st in self.stations]], s=50, c='red', marker='8', transform=ccrs.PlateCarree(), edgecolors='black', zorder=5)
                for coord in active_stations: ax.annotate(text=coord['station'], xy=(coord['longitude'], coord['latitude']), xytext=(5, 5), textcoords='offset points', ha='right', color='white', bbox=dict(boxstyle="round,pad=0.2", fc="black", alpha=0.5), zorder=6)
                
                plotted_items = []
                # Correção: A interpolação 2D precisa de pelo menos 3 pontos.
                if len(lons) < 2:
                    # Cria um objeto de normalização explícito para garantir a escala.
                    norm = Normalize(vmin=self.min_scale, vmax=self.max_scale)
                    # Se tiver apenas 1 ponto, plota o ponto.
                    scatter = ax.scatter(lons, lats, c=vals, cmap=cmap_custom, norm=norm, s=50, transform=ccrs.PlateCarree(), edgecolors='black')
                    mappable = scatter
                    plotted_items.append(scatter)

                else:
                    # Para 2 ou mais pontos, podemos interpolar.
                    lon_grid = np.linspace(self.regiao[0], self.regiao[1], 200)
                    lat_grid = np.linspace(self.regiao[2], self.regiao[3], 200)
                    X, Y = np.meshgrid(lon_grid, lat_grid) # Pontos da grade
                    
                    # Para 3+ pontos, RBF com 'multiquadric' para interpolação suave e máscara com casco convexo.
                    if len(lons) >= 3:
                        # Usa Rbf para uma interpolação mais suave
                        rbfi = Rbf(lons, lats, vals, function='multiquadric')
                        Z = rbfi(X, Y)
                        # Cria uma máscara para plotar apenas dentro da área do casco convexo das estações
                        hull = Delaunay(np.c_[lons, lats])
                        mask = hull.find_simplex(np.c_[X.ravel(), Y.ravel()]) < 0
                        mask = mask.reshape(X.shape)
                        Z[mask] = np.nan
                    # Para 2 pontos, RBF cria um gradiente suave, mas em toda a área.
                    # Usamos RBF para um gradiente suave e uma máscara para limitar a área.
                    else:  # len(lons) == 2
                        # RBF com função linear cria um plano inclinado (gradiente perfeito)
                        rbfi = Rbf(lons, lats, vals, function='linear')
                        Z = rbfi(X, Y)

                        # Para 2 pontos, cria uma máscara de "caminho" para restringir a área.
                        p1 = np.array([lons[0], lats[0]])
                        p2 = np.array([lons[1], lats[1]])
                        p_grid = np.c_[X.ravel(), Y.ravel()]

                        # Projeção para encontrar a distância de cada ponto da grade à linha
                        line_vec = p2 - p1
                        line_len_sq = np.dot(line_vec, line_vec)
                        p_vec = p_grid - p1
                        t = np.dot(p_vec, line_vec) / line_len_sq
                        closest_points = p1 + t[:, np.newaxis] * line_vec
                        dist_to_line = np.linalg.norm(p_grid - closest_points, axis=1)

                        # Define a largura do caminho
                        path_width = max(abs(self.regiao[1] - self.regiao[0]), abs(self.regiao[3] - self.regiao[2])) / 50.0
                        
                        # Máscara: mantém pontos dentro do caminho E estritamente entre as estações.
                        mask = (dist_to_line > path_width) | (t < 0) | (t > 1)
                        Z[mask.reshape(X.shape)] = np.nan

                    Z_masked = np.ma.masked_invalid(Z)
                    norm = Normalize(vmin=self.min_scale, vmax=self.max_scale)
                    if len(lons) == 2:
                        # Usa pcolormesh para o efeito de "quadrados" que não vaza para fora.
                        contour = ax.pcolormesh(X, Y, Z_masked, cmap=cmap_custom, norm=norm, transform=ccrs.PlateCarree(), shading='auto')
                    else:
                        # Usa contourf para 3+ estações, onde ele funciona bem.
                        # A máscara do casco convexo já limita a área de dados. O clipping adicional estava causando o erro.
                        contour = ax.contourf(X, Y, Z_masked, levels=100, cmap=cmap_custom, norm=norm, transform=ccrs.PlateCarree())
                        
                        # Adiciona círculos coloridos em volta das estações para 3+ pontos.
                        # O tamanho (s=200) e a borda (edgecolors) garantem a visibilidade.
                        # Correção: zorder=4 para que o círculo fique atrás do marcador da estação (zorder=5) e do nome (zorder=6).
                        ax.scatter(lons, lats, c=vals, s=200, marker='o', cmap=cmap_custom, norm=norm, transform=ccrs.PlateCarree(), edgecolors='white', linewidth=1.5, zorder=4)
                    mappable = contour

                # Adiciona o título após desenhar o contorno
                ax.set_title(f"{self.title}\n{current_time_dt.strftime('%d/%m/%Y %H:%M')} UT", weight='bold')

                from matplotlib.ticker import MaxNLocator
                # Passa o mesmo 'norm' para a colorbar para garantir consistência total.
                cbar = fig.colorbar(mappable, ax=ax, orientation='vertical', shrink=0.6) # O norm já está no mappable
                cbar.set_label(f'Componente {plot_type.upper()} (nT)')
                if self.ticks > 0:
                    # Usa MaxNLocator para distribuir os ticks de forma inteligente, respeitando os limites.
                    locator = MaxNLocator(nbins=self.ticks, prune='both')
                    cbar.locator = locator
                    cbar.update_ticks()

                filename = f"{self.title}_{current_time_dt.strftime('%Y%m%d_%H%M')}.png"
                filepath = os.path.join(output_dir, filename)
                fig.savefig(filepath, dpi=300, bbox_inches='tight')
                images_saved_count += 1

                # Fecha a figura para liberar memória
                plt.close(fig)

                current_time_dt += interval_delta

            current_date_iterator += timedelta(days=1)
        
        if images_saved_count > 0:
            QMessageBox.information(None, "Concluído", f"{images_saved_count} imagem(ns) de contorno salva(s) em:\n{os.path.abspath(output_dir)}")
        else:
            QMessageBox.warning(None, "Nenhuma Imagem Gerada",
                                "Não foi possível gerar as imagens de contorno.\n\n"
                                "Motivo provável: Não foram encontrados dados de estações "
                                "para os intervalos de tempo definidos. Verifique a formatação da hora nos arquivos de dados "
                                "e a disponibilidade dos dados para o período selecionado.")

    
    '''def save_contour_map_sequence(self, map_widget, plot_type):
        import os
        import shutil
        import cartopy.crs as ccrs
        import cartopy.feature as cfeature
        import matplotlib.pyplot as plt
        from matplotlib.colors import LinearSegmentedColormap
        from matplotlib.ticker import MaxNLocator
        from scipy.interpolate import Rbf
        from scipy.spatial import Delaunay
        import numpy as np
        from datetime import datetime, timedelta

        # ----------------------------------------------------------
        # Diretório de saída
        # ----------------------------------------------------------
        output_dir = f"Contour_Maps/{self.title}"
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
        os.makedirs(output_dir, exist_ok=True)

        images_saved_count = 0

        # ----------------------------------------------------------
        # Colormap
        # ----------------------------------------------------------
        cores = [
            (0, 0, 0.5),
            (0, 0.5, 1),
            (1, 1, 0),
            (1, 0.5, 0),
            (1, 0, 0)
        ]
        cmap_custom = LinearSegmentedColormap.from_list("custom_cmap", cores)

        # ----------------------------------------------------------
        # Parse dos horários
        # ----------------------------------------------------------
        start_t = datetime.strptime(self.start_time, "%H:%M").time()
        end_t = datetime.strptime(self.end_time, "%H:%M").time()
        ih, im = [int(x) for x in self.interval.split(':')]
        interval_delta = timedelta(hours=ih, minutes=im)

        current_date = self.start_date
        end_date = self.end_date

        # ----------------------------------------------------------
        # Grade fixa (só dentro da região definida)
        # ----------------------------------------------------------
        RES = 250
        lon_grid = np.linspace(self.regiao[0], self.regiao[1], RES)
        lat_grid = np.linspace(self.regiao[2], self.regiao[3], RES)
        X, Y = np.meshgrid(lon_grid, lat_grid)

        while current_date < end_date:

            day_start = datetime.combine(current_date, start_t)
            day_end = datetime.combine(
                current_date + timedelta(days=1) if end_t < start_t else current_date,
                end_t
            )

            current_time = day_start

            while current_time <= day_end:

                dkey = f"{current_time.day}/{current_time.month}/{current_time.year}"
                tkey = f"{current_time.hour}:{current_time.minute}"

                lons, lats, vals = [], [], []
                active_stations = []

                # ----------------------------------------------------------
                # Coleta dados válidos para o horário corrente
                # ----------------------------------------------------------
                for sname in self.stations:
                    code = sname.split()[0]

                    sdata = self.all_data.get(code, {})
                    if dkey not in sdata:
                        continue

                    time_data = sdata[dkey].get(tkey)
                    if not time_data:
                        continue

                    val = time_data.get(plot_type)
                    if val is None or np.isnan(val):
                        continue

                    info = self.data_with_stations.get(code)
                    full_info = next(
                        (x for x in map_widget.all_locals if x['station'].split()[0] == code),
                        None
                    )
                    if not info or not full_info:
                        continue

                    lons.append(float(info[1]))
                    lats.append(float(info[2]))
                    vals.append(val)
                    active_stations.append(full_info)

                if len(vals) < 2:
                    current_time += interval_delta
                    continue

                # ----------------------------------------------------------
                # Figura
                # ----------------------------------------------------------
                fig = plt.figure(figsize=(10, 8))
                ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
                ax.add_feature(cfeature.LAND)
                ax.add_feature(cfeature.OCEAN)
                ax.add_feature(cfeature.COASTLINE)
                ax.add_feature(cfeature.BORDERS)
                ax.set_extent(self.regiao, crs=ccrs.PlateCarree())

                # ----------------------------------------------------------
                # INTERPOLAÇÃO RBF
                # ----------------------------------------------------------
                rbf = Rbf(lons, lats, vals, function='multiquadric', smooth=0.2)
                Z = rbf(X, Y)

                # ----------------------------------------------------------
                # MÁSCARA DO CONVEX HULL — LIMITA AO CONTORNO DAS ESTAÇÕES
                # ----------------------------------------------------------
                if len(lons) >= 3:
                    hull = Delaunay(np.column_stack([lons, lats]))
                    inside_hull = hull.find_simplex(np.column_stack([X.ravel(), Y.ravel()])) >= 0
                    inside_hull = inside_hull.reshape(X.shape)

                    # --------------------------
                    # REDUÇÃO EXTRA DA ÁREA ÚTIL
                    # aplica um “shrink” interno
                    # --------------------------
                    from scipy.ndimage import binary_erosion

                    shrink_steps = 8   # <-- ajuste para mais/menos recuo
                    inside_shrunk = binary_erosion(inside_hull, iterations=shrink_steps)

                    Z = Z.copy()
                    Z[~inside_shrunk] = np.nan


                # ----------------------------------------------------------
                # CASO 2 PONTOS — máscara estreita entre eles
                # ----------------------------------------------------------
                elif len(lons) == 2:
                    p1 = np.array([lons[0], lats[0]])
                    p2 = np.array([lons[1], lats[1]])
                    dist = np.linalg.norm(p1 - p2)

                    pts = np.column_stack([X.ravel(), Y.ravel()])
                    mask = (
                        np.linalg.norm(pts - p1, axis=1) +
                        np.linalg.norm(pts - p2, axis=1)
                    ) <= dist * 1.3   # faixa estreita entre as duas estações

                    Z = Z.copy()
                    Z[~mask.reshape(X.shape)] = np.nan


                # ----------------------------------------------------------
                # 1 PONTO — sem contorno
                # ----------------------------------------------------------
                else:
                    Z[:] = np.nan


                # ----------------------------------------------------------
                # PLOT DO CONTORNO
                # ----------------------------------------------------------
                Z = np.ma.masked_invalid(Z)
                contour = ax.contourf(
                    X, Y, Z, 100, cmap=cmap_custom,
                    vmin=self.min_scale, vmax=self.max_scale,
                    transform=ccrs.PlateCarree()
                )

                # ----------------------------------------------------------
                # INCLUIR OS PONTOS DAS ESTAÇÕES NO MAPA
                # ----------------------------------------------------------
                ax.scatter(
                    lons, lats, s=50,
                    c='black', edgecolors='white', linewidth=1.2,
                    transform=ccrs.PlateCarree(), zorder=5
                )

                for i in range(len(lons)):
                    ax.text(
                        lons[i] + 0.05, lats[i] + 0.05,
                        active_stations[i]['station'],
                        transform=ccrs.PlateCarree(),
                        fontsize=8, weight='bold',
                        color='white', bbox=dict(fc='black', alpha=0.65, pad=1)
                    )


                # ----------------------------------------------------------
                # COLORBAR 100% fiel aos parâmetros do usuário
                # ----------------------------------------------------------
                cbar = fig.colorbar(contour, ax=ax, shrink=0.65, orientation="vertical")
                cbar.set_label(f'Componente {plot_type.upper()} (nT)')

                if self.ticks > 1:
                    locator = MaxNLocator(nbins=self.ticks)
                    cbar.locator = locator
                    cbar.update_ticks()

                # ----------------------------------------------------------
                # Título e salvamento
                # ----------------------------------------------------------
                ax.set_title(f"{self.title}\n{current_time.strftime('%d/%m/%Y %H:%M')} UT", weight='bold')

                fname = f"{self.title}_{current_time.strftime('%Y%m%d_%H%M')}.png"
                fig.savefig(os.path.join(output_dir, fname), dpi=300, bbox_inches='tight')
                plt.close(fig)

                images_saved_count += 1
                current_time += interval_delta

            current_date += timedelta(days=1)

        # Mensagem
        if images_saved_count > 0:
            QMessageBox.information(None, "Concluído", f"{images_saved_count} imagens salvas em:\n{os.path.abspath(output_dir)}")
        else:
            QMessageBox.warning(None, "Nenhuma Imagem", "Não foi possível gerar imagens para os intervalos selecionados.")'''



    def add_delta_dict(self, type):
        base_type = type.replace('d', '')
        delta = self.calculate_midnight_average(base_type)


        for station, st in zip(self.stations, range(len(self.stations))):
            for day, times in self.all_data[station].items():
                for time in times:
                    date = times[time].get(base_type)
                    self.all_data[station][day][time][type] = date - delta[st] if date is not None else None
                    
    # add reference line for dH line 
    def add_reference(self, selected_types):
        for type in selected_types:
            if 'reference' in type:
                base_type = type.replace('-reference', '')
                delta = self.calculate_midnight_average_reference(base_type)
                calm_averages = self.calculate_reference(base_type)

                for station in self.stations:
                    for day, times in self.all_data[station].items():
                        for t, time in enumerate(times):
                            self.all_data[station][day][time][type] = calm_averages[t] - delta if calm_averages[t] is not None else None

    def add_plots(self, slct_types):
        try:
            import matplotlib as mpl
            from matplotlib.colors import LinearSegmentedColormap

            plt.close('all')
            self.fig, self.ax = plt.subplots()

            if isinstance(self.start_date, QDate):
                self.start_date = self.start_date.toPyDate()
            if isinstance(self.end_date, QDate):
                self.end_date = self.end_date.toPyDate()

            self.filtred_values = []
            self.current_contour = None
            self._current_cbar = None

            # cria colormap personalizado
            cores = [
                (1, 0, 0),       # vermelho
                (1, 0.5, 0),     # laranja
                (1, 1, 0),       # amarelo
                (0, 0.5, 1),     # azul claro
                (0, 0, 0.5)      # azul escuro
            ]
            cmap_custom = LinearSegmentedColormap.from_list("vermelho_laranja_amarelo_azul", cores)

            for plot_type in slct_types:
                times_all, lats_all, vals_all = [], [], []

                for station in self.stations:
                    station_code = station.split()[0]
                    if station_code not in self.data_with_stations:
                        continue

                    station_lat = float(self.data_with_stations[station_code][2])
                    if station_code not in self.all_data:
                        continue

                    for day_str, times in self.all_data[station_code].items():
                        day_date = datetime.strptime(day_str, "%d/%m/%Y").date()
                        for time_str, data_dict in times.items():
                            val = data_dict.get(plot_type)
                            if val is not None:
                                time_obj = datetime.strptime(time_str, "%H:%M").time()
                                dt = datetime.combine(day_date, time_obj)
                                times_all.append(dt)
                                lats_all.append(station_lat)
                                vals_all.append(val)
                                self.filtred_values.append(val)

                if not vals_all:
                    QMessageBox.information(
                        None,
                        self.util.dict_language[self.lang]["mgbox_error"],
                        f"Sem dados para {plot_type} no período selecionado."
                    )
                    self.can_plot = False
                    return

                times_num = mdates.date2num(times_all)
                lats_arr = np.array(lats_all, dtype=float)
                vals_arr = np.array(vals_all, dtype=float)

                # Aumenta a resolução da grade para uma interpolação mais precisa
                time_grid = np.linspace(times_num.min(), times_num.max(), 1000) # Mais pontos no tempo
                lat_grid = np.linspace(lats_arr.min(), lats_arr.max(), max(100, len(np.unique(lats_arr))*10)) # Mais pontos na latitude
                X, Y = np.meshgrid(time_grid, lat_grid)

                if len(np.unique(lats_arr)) == 1:
                    # caso de uma estação
                    lat = np.unique(lats_arr)[0]
                    X, Y = np.meshgrid(time_grid, [lat - 0.001, lat + 0.001])
                    vals_interp = np.interp(time_grid, times_num, vals_arr) # Simplificado
                    Z = np.tile(vals_interp, (2, 1))
                else:
                    # Usa interpolação linear, que é mais robusta para dados esparsos e menos propensa a NaNs que a cúbica.
                    Z = griddata((times_num, lats_arr), vals_arr, (X, Y), method='linear')

                if Z is None or np.all(np.isnan(Z)):
                    QMessageBox.information(
                        None,
                        self.util.dict_language[self.lang]["mgbox_error"],
                        f"Não foi possível interpolar valores para {plot_type} (poucos pontos)."
                    )
                    self.can_plot = False
                    return

                Z_masked = np.ma.masked_invalid(Z)
                contour = self.ax.contourf(X, Y, Z_masked, levels=100, cmap=cmap_custom.reversed())
                self.current_contour = contour
                # salva limites originais do contorno
                if not hasattr(self, '_original_clim') or self._original_clim is None:
                    self._original_clim = contour.get_clim()

                cbar = self.fig.colorbar(contour, ax=self.ax, orientation='vertical')
                self._current_cbar = cbar

                station_lats = []
                station_labels = []
                for station in self.stations:
                    code = station.split()[0]
                    info = self.data_with_stations.get(code, None)
                    if info:
                        station_lats.append(float(info[2]))  # latitude
                        station_labels.append(code)          # código da estação

                # opcional: ordenar por latitude
                station_lats = np.array(station_lats, dtype=float)
                order = np.argsort(station_lats)
                ordered_lats = station_lats[order]
                ordered_labels = [station_labels[i] for i in order]

                self.ax.set_yticks(ordered_lats.tolist())
                self.ax.set_yticklabels([f"{label} ({lat:.2f})" for label, lat in zip(ordered_labels, ordered_lats)])

            # função para abrir diálogo de limites
            def open_color_limits_dialog():
                dlg = QDialog()
                dlg.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)
                dlg.setWindowTitle("Ajustar limites de cor")
                layout = QVBoxLayout(dlg)

                current_vmin, current_vmax = self.current_contour.get_clim()
                lbl_min = QLabel("Valor mínimo:")
                le_min = QLineEdit(f"{current_vmin:.6g}")
                lbl_max = QLabel("Valor máximo:")
                le_max = QLineEdit(f"{current_vmax:.6g}")

                row_min = QHBoxLayout(); row_min.addWidget(lbl_min); row_min.addWidget(le_min)
                row_max = QHBoxLayout(); row_max.addWidget(lbl_max); row_max.addWidget(le_max)
                layout.addLayout(row_min)
                layout.addLayout(row_max)

                # botões
                btn_ok = QPushButton("OK")
                btn_cancel = QPushButton("Cancelar")
                btn_reset = QPushButton("Reset")
                btn_row = QHBoxLayout(); btn_row.addStretch(1)
                btn_row.addWidget(btn_ok); btn_row.addWidget(btn_cancel); btn_row.addWidget(btn_reset)
                layout.addLayout(btn_row)

                def on_ok():
                    try:
                        vmin, vmax = float(le_min.text()), float(le_max.text())
                    except ValueError:
                        return
                    if vmin < vmax:
                        self.current_contour.set_clim(vmin, vmax)
                        self._current_cbar.update_normal(self.current_contour)
                        vmin, vmax = float(le_min.text()), float(le_max.text())
                        if vmin < vmax:
                            self.current_contour.set_clim(vmin, vmax)       # atualiza contorno
                            self._current_cbar.update_normal(self.current_contour)  # atualiza cores
                            self._current_cbar.set_ticks(np.linspace(vmin, vmax, 10))  # recalcula ticks automáticos
                            self.fig.canvas.draw_idle()
                        dlg.close()

                def on_reset():
                    vmin = self._original_clim[0]
                    vmax = self._original_clim[1]
                    self.current_contour.set_clim(vmin, vmax)
                    self._current_cbar.update_normal(self.current_contour)
                    self._current_cbar.set_ticks(np.linspace(vmin, vmax, 10))
                    le_min.setText(f"{vmin:.6g}")  
                    le_max.setText(f"{vmax:.6g}")
                    self.fig.canvas.draw_idle()   
                    dlg.close()

                btn_ok.clicked.connect(on_ok)
                btn_cancel.clicked.connect(dlg.close)
                btn_reset.clicked.connect(on_reset)

                dlg.show()

            # evento de clique na colorbar
            def on_click(event):
                if event.inaxes is self._current_cbar.ax:
                    open_color_limits_dialog()

            self.fig.canvas.mpl_connect("button_press_event", on_click)

        except Exception as error:
            QMessageBox.information(
                None,
                self.util.dict_language[self.lang]["mgbox_error"],
                self.util.dict_language[self.lang]["mgbox_error_plt_st"]
            )
            self.can_plot = False


    def config_graph(self, plot_type):
        # configura eixo X (tempo diário)
        self.ax.xaxis.set_major_locator(mdates.DayLocator())  
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%d'))
        self.ax.xaxis.set_minor_locator(mdates.HourLocator(interval=3))
        self.ax.tick_params(axis='x', which='minor', labelbottom=False)
        #self.fig.autofmt_xdate()
        #self.ax.xaxis.set_minor_locator(mdates.MinuteLocator(interval=30))

        self.ax.set_xlim(self.start_date, self.end_date)
        self.ax.set_xlabel('UT (Dias)')
        self.ax.set_ylabel('Latitude das Estações')
        period_str = f"{self.start_date.strftime('%d/%m/%Y')} - { (self.end_date - timedelta(days=1)).strftime('%d/%m/%Y') }"
        self.ax.set_title(f'{", ".join(plot_type)} | {period_str}')

        if self.bold_text:
            self.ax.xaxis.label.set_weight('bold')
            self.ax.yaxis.label.set_weight('bold')
            self.ax.title.set_weight('bold')
            for label in self.ax.get_xticklabels() + self.ax.get_yticklabels():
                label.set_fontweight('bold')

        if self.grid_graph:
            self.ax.grid(True, linestyle='-', alpha=1, which='major', color='black', linewidth=1)

    