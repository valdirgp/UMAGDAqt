import requests
import pandas as pd
from datetime import datetime
import os
import io

class GeoIndexHandler:
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(GeoIndexHandler, cls).__new__(cls)
        return cls._instance

    def __init__(self, cache_file='geo_indices.txt'):
        if hasattr(self, 'initialized') and self.initialized:
            return
            
        self.url = "https://kp.gfz.de/app/files/Kp_ap_Ap_SN_F107_since_1932.txt"
        self.cache_file = cache_file
        self.df = None
        self._load_data()
        self.initialized = True

    def _download_data(self):
        try:
            response = requests.get(self.url)
            response.raise_for_status()
            with open(self.cache_file, 'w') as f:
                f.write(response.text)
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error downloading geo index data: {e}")
            return None

    def _load_data(self):
        # ------------------------------------------------------------------
        # Load raw text
        # ------------------------------------------------------------------
        if os.path.exists(self.cache_file):
            with open(self.cache_file, 'r') as f:
                data_text = f.read()
        else:
            data_text = self._download_data()

        if not data_text:
            print("Could not load geo index data.")
            return

        # ------------------------------------------------------------------
        # Skip header
        # ------------------------------------------------------------------
        lines = data_text.strip().split('\n')
        data_start_line = 0
        for i, line in enumerate(lines):
            if not line.startswith('#'):
                data_start_line = i
                break

        data_io = io.StringIO('\n'.join(lines[data_start_line:]))

        # ------------------------------------------------------------------
        # Column names (GFZ official format)
        # ------------------------------------------------------------------
        col_names = [
            'Year', 'Month', 'Day', 'days', 'days_m', 'Bsr', 'dB',
            'Kp1', 'Kp2', 'Kp3', 'Kp4', 'Kp5', 'Kp6', 'Kp7', 'Kp8',
            'ap1', 'ap2', 'ap3', 'ap4', 'ap5', 'ap6', 'ap7', 'ap8',
            'Ap', 'SN', 'F10.7_obs', 'F10.7_adj', 'D'
        ]

        daily_df = pd.read_csv(
            data_io,
            sep=r'\s+',
            engine='python',
            names=col_names,
            na_values=['-1', '-1.0', -1, -1.0, '***.**']
        )

        # ------------------------------------------------------------------
        # Date handling
        # ------------------------------------------------------------------
        for col in ['Year', 'Month', 'Day']:
            daily_df[col] = pd.to_numeric(daily_df[col], errors='coerce').astype('Int64')

        daily_df['Date'] = pd.to_datetime(daily_df[['Year', 'Month', 'Day']])
        daily_df.set_index('Date', inplace=True)

        # ------------------------------------------------------------------
        # CORREÇÃO 2: F10.7A = média centrada de 81 dias (observado)
        # ------------------------------------------------------------------
        daily_df['f107a'] = daily_df['F10.7_obs'].rolling(
            window=81,
            center=True,
            min_periods=1  # Permite o cálculo nas bordas do conjunto de dados
        ).mean()

        # ------------------------------------------------------------------
        # Unpivot Kp and ap (3h resolution)
        # ------------------------------------------------------------------
        kp_df = pd.melt(
            daily_df.reset_index(),
            id_vars=['Date'],
            value_vars=[f'Kp{i}' for i in range(1, 9)],
            var_name='Kp_block',
            value_name='Kp_float'  # Nome temporário para o valor com decimais
        ).assign(
            hour_block=lambda x: (x['Kp_block'].str[2:].astype(int) - 1) * 3,
            Kp=lambda x: x['Kp_float']  # Mantém precisão decimal do Kp
        )

        # ------------------------------------------------------------------
        # CORREÇÃO CRUCIAL: Mapear os valores diários para o dataframe de 3h.
        # Isso garante que a ordem dos blocos de Kp seja preservada.
        # ------------------------------------------------------------------
        final_df = kp_df.copy()
        final_df['ap'] = final_df['Date'].map(daily_df['Ap'])
        final_df['f107a'] = final_df['Date'].map(daily_df['f107a'])
        final_df['F10.7_obs'] = final_df['Date'].map(daily_df['F10.7_obs'])

        # ------------------------------------------------------------------
        # Build datetime index (3h resolution)
        # ------------------------------------------------------------------
        final_df['datetime'] = final_df.apply(
            lambda row: row['Date'] + pd.to_timedelta(row['hour_block'], unit='h'),
            axis=1
        )

        final_df.set_index('datetime', inplace=True)
        self.df = final_df

    def get_indices(self, dt_obj):
        """
        Returns the indices exactly as required by Anderson et al. (2004)
        """
        try:
            kp_index = dt_obj.hour // 3
            target_datetime = dt_obj.replace(
                hour=kp_index * 3,
                minute=0,
                second=0,
                microsecond=0
            )

            row = self.df.loc[target_datetime]

            return {
                'f107': row['F10.7_obs'],   # observado diário
                'f107a': row['f107a'],     # média 81 dias
                'ap': row['ap'],           # Ap diário
                'kp': row['Kp']            # Kp de 3h (como na fórmula)
            }

        except KeyError:
            return None
