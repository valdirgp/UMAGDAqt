import os
import shutil
import cartopy.crs as ccrs
from Model.GraphPage.GraphsModule import GraphsModule
from Model.Custom.CustomPltOptions import CustomPltOptions
from General.util import Util
from datetime import datetime, timedelta
from PyQt5.QtWidgets import QMessageBox
import numpy as np
from scipy.interpolate import griddata, Rbf
from scipy.spatial import Delaunay
from matplotlib.colors import Normalize

from PyQt5.QtWidgets import QMessageBox

class MapGraph(GraphsModule):
    def __init__(self, root, language):
        self.root = root
        self.lang = language
        self.util = Util()
        super().__init__(self.lang)

    def plot_map_contour(self, local_downloaded, stations, selected_types, bold_text, grid_graph,

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
            xlim = map_widget.ax.get_xlim()
            ylim = map_widget.ax.get_ylim()
            self.saved_extent = [float(xlim[0]), float(xlim[1]), float(ylim[0]), float(ylim[1])]

            self.regiao = self.saved_extent

            self.title = str(contornoMap[0])
            # Correção: Converter os valores de escala para float.
            self.min_scale = float(contornoMap[1])

            self.max_scale = float(contornoMap[2])

            self.ticks = int(contornoMap[3])

            self.start_time = str(contornoMap[4])

            self.end_time = str(contornoMap[5])

            self.interval = str(contornoMap[6])

            self.name_station = bool(contornoMap[7])

            self.pontos_station = bool(contornoMap[8])

            self.save_contour_map_sequence(map_widget, selected_types[0])
    
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

                day_str_lookup = f"{current_time_dt.day}/{current_time_dt.month}/{current_time_dt.year}" 
                time_str_lookup = f"{current_time_dt.hour}:{current_time_dt.minute}"

                lons, lats, vals, active_stations = [], [], [], []
                for station_full_name in self.stations:
                    station_code = station_full_name.split()[0]
                    station_data = self.all_data.get(station_code, {})
                    if day_str_lookup in station_data:
                        time_data = station_data[day_str_lookup].get(time_str_lookup)
                        
                        if time_data and time_data.get(plot_type) is not None:
                            info = self.data_with_stations.get(station_code)
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
                #ax.scatter([s['longitude'] for s in map_widget.all_locals if s['station'].split()[0] in [st.split()[0] for st in self.stations]], [s['latitude'] for s in map_widget.all_locals if s['station'].split()[0] in [st.split()[0] for st in self.stations]], s=50, c='red', marker='8', transform=ccrs.PlateCarree(), edgecolors='black', zorder=5)
                if self.name_station:
                    for coord in active_stations: ax.annotate(text=coord['station'], xy=(coord['longitude'], coord['latitude']), xytext=(5, 5), textcoords='offset points', ha='right', color='white', bbox=dict(boxstyle="round,pad=0.2", fc="black", alpha=0.5), zorder=6)
                
                plotted_items = []
                if len(lons) < 2:
                    # Cria um objeto de normalização explícito para garantir a escala.
                    norm = Normalize(vmin=self.min_scale, vmax=self.max_scale)
                    # Se tiver apenas 1 ponto, plota o ponto.
                    if self.pontos_station:
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
                    if self.pontos_station:
                        ax.scatter(lons, lats, c=vals, s=200, marker='o', cmap=cmap_custom, norm=norm, transform=ccrs.PlateCarree(), edgecolors='white', linewidth=1.5, zorder=4)
                    mappable = contour

                ax.set_title(f"{self.title}\n{current_time_dt.strftime('%d/%m/%Y %H:%M')} UT", weight='bold')

                from matplotlib.ticker import MaxNLocator
                cbar = fig.colorbar(mappable, ax=ax, orientation='vertical', shrink=0.6) # O norm já está no mappable
                cbar.set_label(f'Componente {plot_type.upper()} (nT)')
                if self.ticks > 0:
                    locator = MaxNLocator(nbins=self.ticks, prune='both')
                    cbar.locator = locator
                    cbar.update_ticks()

                filename = f"{self.title}_{current_time_dt.strftime('%Y%m%d_%H%M')}.png"
                filepath = os.path.join(output_dir, filename)
                fig.savefig(filepath, dpi=300, bbox_inches='tight')
                images_saved_count += 1

                plt.close(fig)

                current_time_dt += interval_delta

            current_date_iterator += timedelta(days=1)
        
        if images_saved_count > 0:
            QMessageBox.information(None, self.util.dict_language[self.lang]["mgbox_success"], f"{images_saved_count} {self.util.dict_language[self.lang]['mgbox_imagens_salvas']}\n{os.path.abspath(output_dir)}")
        else:
            QMessageBox.warning(None, self.util.dict_language[self.lang]["mgbox_error"],
                                self.util.dict_language[self.lang]['mgbox_imagens_nao_geradas'])
    


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