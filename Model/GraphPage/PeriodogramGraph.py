'''from Model.GraphPage.GraphsModule import GraphsModule
import matplotlib.pyplot as plt
import re
import os
import csv
import numpy as np
from astropy.timeseries import LombScargle

class PeriodogramGraph(GraphsModule):
    """Lomb-Scargle periodogram for external TXT/CSV files."""

    def __init__(self, root, language):
        self.root = root
        self.lang = language

        self.files = []
        self.start_hour = 0.0
        self.end_hour = 24.0
        self.results = {}
        super().__init__(self.lang)

    def plot_periodogram(self, files=None, start_hour=0.0, end_hour=24.0, bold=False, grid=False):
        if files is not None:
            self.files = self._normalize_files(files)

        self.start_hour = self._time_to_decimal(start_hour)
        self.end_hour = self._time_to_decimal(end_hour)

        if not 0 <= self.start_hour <= 24 or not 0 <= self.end_hour <= 24:
            raise ValueError("Start/end hour must be between 0 and 24.")
        if self.start_hour > self.end_hour:
            raise ValueError("Start hour cannot be greater than end hour.")
        if not self.files:
            raise ValueError("No files were selected.")

        self.results = {}
        for path in self.files:
            try:
                times, values = self.read_file(path)
                times, values = self.filter_data(times, values)
                if len(times) < 3:
                    raise ValueError("At least 3 valid samples are required in the selected interval.")

                period, power, frequency = self.calculate_periodogram(times, values)
                self.results[path] = {
                    "file": path,
                    "label": os.path.basename(path),
                    "time": times,
                    "value": values,
                    "period_hours": period,
                    "frequency_per_hour": frequency,
                    "power": power,
                    "error": None,
                }
            except Exception as exc:
                self.results[path] = {
                    "file": path,
                    "label": os.path.basename(path),
                    "error": str(exc),
                }

        self.show_graph(bold, grid)

        return self.results

    @staticmethod
    def _normalize_files(files):
        if isinstance(files, (str, os.PathLike)):
            return [str(files)]
        return [str(path) for path in files if path]

    @staticmethod
    def _time_to_decimal(value):
        if value is None:
            return 0.0
        if isinstance(value, (int, float, np.number)):
            return float(value)

        if hasattr(value, "hour") and hasattr(value, "minute"):
            hour_attr = value.hour
            minute_attr = value.minute
            second_attr = getattr(value, "second", None)
            hour = hour_attr() if callable(hour_attr) else hour_attr
            minute = minute_attr() if callable(minute_attr) else minute_attr
            second = 0 if second_attr is None else (second_attr() if callable(second_attr) else second_attr)
            return float(hour) + float(minute) / 60.0 + float(second) / 3600.0

        text = str(value).strip().replace(",", ".")
        if ":" in text:
            pieces = text.split(":")
            if len(pieces) not in (2, 3):
                raise ValueError(f"Invalid time: {value}")
            hour = float(pieces[0])
            minute = float(pieces[1])
            second = float(pieces[2]) if len(pieces) == 3 else 0.0
            return hour + minute / 60.0 + second / 3600.0
        return float(text)

    @staticmethod
    def _to_float(value):
        text = str(value).strip().strip('"').strip("'")
        if not text:
            raise ValueError("Empty value.")
        return float(text.replace(",", "."))

    def read_file(self, path):
        if not os.path.isfile(path):
            raise FileNotFoundError(path)
        extension = os.path.splitext(path)[1].lower()
        if extension not in (".txt", ".csv"):
            raise ValueError("Only TXT and CSV files are supported.")

        times, values = [], []
        with open(path, "r", encoding="utf-8-sig", errors="replace", newline="") as handle:
            for raw_line in handle:
                parsed = self._parse_csv_line(raw_line) if extension == ".csv" else self._parse_txt_line(raw_line)
                if parsed is None:
                    continue
                hour, mean = parsed
                if np.isfinite(hour) and np.isfinite(mean):
                    times.append(hour)
                    values.append(mean)

        if not times:
            raise ValueError("No rows containing both a valid time and a valid mean were found.")

        times = np.asarray(times, dtype=float)
        values = np.asarray(values, dtype=float)
        order = np.argsort(times)
        return times[order], values[order]

    def _parse_csv_line(self, raw_line):
        line = raw_line.strip("\r\n")
        if not line.strip():
            return None
        fields = next(csv.reader([line], delimiter=";", quotechar='"'))
        return self._extract_first_and_last(fields)

    def _parse_txt_line(self, raw_line):
        line = raw_line.strip("\r\n")
        if not line.strip():
            return None
        fields = [field for field in re.split(r"[\t ]+", line.strip()) if field]
        return self._extract_first_and_last(fields)

    def _extract_first_and_last(self, fields):
        non_empty = [str(field).strip() for field in fields if str(field).strip()]
        if len(non_empty) < 2:
            return None
        try:
            return self._to_float(non_empty[0]), self._to_float(non_empty[-1])
        except (TypeError, ValueError):
            return None

    def filter_data(self, times, values):
        times = np.asarray(times, dtype=float)
        values = np.asarray(values, dtype=float)
        valid = (np.isfinite(times) & np.isfinite(values) &
                 (times >= self.start_hour) & (times <= self.end_hour))
        return times[valid], values[valid]

    def calculate_periodogram(self, times, values):
        times = np.asarray(times, dtype=float)
        values = np.asarray(values, dtype=float)
        if times.size < 3:
            raise ValueError("Not enough samples for Lomb-Scargle.")

        unique_times, inverse = np.unique(times, return_inverse=True)
        if unique_times.size != times.size:
            sums = np.zeros(unique_times.size, dtype=float)
            counts = np.zeros(unique_times.size, dtype=int)
            np.add.at(sums, inverse, values)
            np.add.at(counts, inverse, 1)
            times = unique_times
            values = sums / counts

        if times.size < 3:
            raise ValueError("Not enough unique timestamps for Lomb-Scargle.")

        span = float(np.max(times) - np.min(times))
        if span <= 0:
            raise ValueError("The selected data has no time span.")

        diffs = np.diff(np.sort(times))
        diffs = diffs[diffs > 0]
        if diffs.size == 0:
            raise ValueError("Unable to determine sampling interval.")

        cadence = float(np.median(diffs))
        minimum_frequency = 1.0 / span
        maximum_frequency = 0.5 / cadence
        if maximum_frequency <= minimum_frequency:
            maximum_frequency = minimum_frequency * 2.0

        model = LombScargle(times, values, center_data=True, fit_mean=True)
        frequency, power = model.autopower(
            minimum_frequency=minimum_frequency,
            maximum_frequency=maximum_frequency,
            samples_per_peak=10,
        )

        valid = np.isfinite(frequency) & np.isfinite(power) & (frequency > 0)
        frequency, power = frequency[valid], power[valid]
        if frequency.size == 0:
            raise ValueError("Lomb-Scargle did not produce valid frequencies.")

        period = 1.0 / frequency
        order = np.argsort(period)
        return period[order], power[order], frequency[order]

    def show_graph(self, bold, grid):
        plt.close("all")
        fig, ax = plt.subplots(figsize=(10, 6))

        plotted = 0

        for result in self.results.values():
            if result.get("error") is not None:
                continue

            ax.plot(
                result["period_hours"],
                result["power"],
                linewidth=1.2,
                label=result["label"]
            )

            plotted += 1

        if plotted == 0:
            plt.close(fig)
            raise RuntimeError("No valid periodograms were generated.")

        ax.set_title("Lomb-Scargle Periodogram")
        ax.set_xlabel("Period (hours)")
        ax.set_ylabel("Power")
        ax.grid(grid, alpha=0.3)
        if bold:
            ax.xaxis.label.set_weight('bold')
            ax.yaxis.label.set_weight('bold')
            ax.title.set_weight('bold')
            for label in ax.get_xticklabels() + ax.get_yticklabels():
                label.set_fontweight('bold')

        ax.legend()

        fig.tight_layout()

        plt.show()

    def get_export_data(self):
        exported = {}
        for path, result in self.results.items():
            if result.get("error") is not None:
                continue
            exported[path] = {
                "period_hours": result["period_hours"].tolist(),
                "frequency_per_hour": result["frequency_per_hour"].tolist(),
                "power": result["power"].tolist(),
            }
        return exported

    def get_errors(self):
        return {path: result["error"] for path, result in self.results.items() if result.get("error") is not None}

    def clear_graph(self):
        self.results = {}'''

from Model.GraphPage.GraphsModule import GraphsModule
import matplotlib.pyplot as plt
import re
import os
import csv
import numpy as np
import pandas as pd
from astropy.timeseries import LombScargle

class PeriodogramGraph(GraphsModule):
    """Lomb-Scargle periodogram for external TXT, CSV and XLSX files."""

    def __init__(self, root, language):
        self.root = root
        self.lang = language

        self.files = []
        self.start_hour = 0.0
        self.end_hour = 24.0
        self.results = {}
        super().__init__(self.lang)

    def plot_periodogram(self, files=None, start_hour=0.0, end_hour=24.0, bold=False, grid=False):
        if files is not None:
            self.files = self._normalize_files(files)

        self.start_hour = self._time_to_decimal(start_hour)
        self.end_hour = self._time_to_decimal(end_hour)

        if not 0 <= self.start_hour <= 24 or not 0 <= self.end_hour <= 24:
            raise ValueError("Start/end hour must be between 0 and 24.")
        if self.start_hour > self.end_hour:
            raise ValueError("Start hour cannot be greater than end hour.")
        if not self.files:
            raise ValueError("No files were selected.")

        self.results = {}

        for path in self.files:
            extension = os.path.splitext(path)[1].lower()

            try:
                # TXT/CSV contain one dataset per file.
                if extension in (".txt", ".csv"):
                    datasets = [(path, os.path.basename(path))]

                # XLSX can contain several worksheets. Each worksheet is
                # treated as an independent dataset.
                elif extension == ".xlsx":
                    datasets = [
                        (f"{path}::{sheet}", f"{os.path.basename(path)} - {sheet}")
                        for sheet in pd.ExcelFile(path).sheet_names
                    ]
                else:
                    raise ValueError(
                        "Unsupported file format. Use TXT, CSV or XLSX files."
                    )

                for dataset_path, label in datasets:
                    try:
                        if extension == ".xlsx":
                            sheet = dataset_path.split("::", 1)[1]
                            times, values = self.read_xlsx_sheet(path, sheet)
                        else:
                            times, values = self.read_file(path)

                        times, values = self.filter_data(times, values)

                        if len(times) < 3:
                            raise ValueError(
                                "At least 3 valid samples are required in the selected interval."
                            )

                        period, power, frequency = self.calculate_periodogram(
                            times, values
                        )

                        self.results[dataset_path] = {
                            "file": path,
                            "sheet": sheet if extension == ".xlsx" else None,
                            "label": label,
                            "time": times,
                            "value": values,
                            "period_hours": period,
                            "frequency_per_hour": frequency,
                            "power": power,
                            "error": None,
                        }

                    except Exception as exc:
                        self.results[dataset_path] = {
                            "file": path,
                            "sheet": sheet if extension == ".xlsx" else None,
                            "label": label,
                            "error": str(exc),
                        }

            except Exception as exc:
                self.results[path] = {
                    "file": path,
                    "sheet": None,
                    "label": os.path.basename(path),
                    "error": str(exc),
                }

        self.show_graph(bold, grid)

        return self.results

    @staticmethod
    def _normalize_files(files):
        if isinstance(files, (str, os.PathLike)):
            return [str(files)]
        return [str(path) for path in files if path]

    @staticmethod
    def _time_to_decimal(value):
        if value is None:
            return 0.0
        if isinstance(value, (int, float, np.number)):
            return float(value)

        if hasattr(value, "hour") and hasattr(value, "minute"):
            hour_attr = value.hour
            minute_attr = value.minute
            second_attr = getattr(value, "second", None)
            hour = hour_attr() if callable(hour_attr) else hour_attr
            minute = minute_attr() if callable(minute_attr) else minute_attr
            second = 0 if second_attr is None else (second_attr() if callable(second_attr) else second_attr)
            return float(hour) + float(minute) / 60.0 + float(second) / 3600.0

        text = str(value).strip().replace(",", ".")
        if ":" in text:
            pieces = text.split(":")
            if len(pieces) not in (2, 3):
                raise ValueError(f"Invalid time: {value}")
            hour = float(pieces[0])
            minute = float(pieces[1])
            second = float(pieces[2]) if len(pieces) == 3 else 0.0
            return hour + minute / 60.0 + second / 3600.0
        return float(text)

    @staticmethod
    def _to_float(value):
        text = str(value).strip().strip('"').strip("'")
        if not text:
            raise ValueError("Empty value.")
        return float(text.replace(",", "."))

    def read_file(self, path):
        if not os.path.isfile(path):
            raise FileNotFoundError(path)

        extension = os.path.splitext(path)[1].lower()

        if extension == ".xlsx":
            # For XLSX files, process the first worksheet by default.
            # plot_periodogram() processes every worksheet individually.
            sheets = pd.ExcelFile(path).sheet_names
            if not sheets:
                raise ValueError("The XLSX file does not contain any worksheets.")
            return self.read_xlsx_sheet(path, sheets[0])

        if extension not in (".txt", ".csv"):
            raise ValueError("Only TXT, CSV and XLSX files are supported.")

        times, values = [], []

        with open(
            path, "r", encoding="utf-8-sig", errors="replace", newline=""
        ) as handle:
            for raw_line in handle:
                parsed = (
                    self._parse_csv_line(raw_line)
                    if extension == ".csv"
                    else self._parse_txt_line(raw_line)
                )

                if parsed is None:
                    continue

                hour, mean = parsed

                if np.isfinite(hour) and np.isfinite(mean):
                    times.append(hour)
                    values.append(mean)

        if not times:
            raise ValueError(
                "No rows containing both a valid time and a valid mean were found."
            )

        times = np.asarray(times, dtype=float)
        values = np.asarray(values, dtype=float)

        order = np.argsort(times)
        return times[order], values[order]

    def read_xlsx_sheet(self, path, sheet_name):
        """
        Reads one XLSX worksheet.

        Expected structure:
            - first column: time
            - one numeric data column: values used by Lomb-Scargle
            - optional additional/categorical columns are ignored

        For the supplied PALMAS file, for example:
            Time | foEs | Es

        'Time' is used as X and 'foEs' as Y. The 'Es' column is ignored
        because it is not a numeric measurement column.
        """
        if not os.path.isfile(path):
            raise FileNotFoundError(path)

        df = pd.read_excel(path, sheet_name=sheet_name)

        if df.empty:
            raise ValueError(f"Worksheet '{sheet_name}' is empty.")

        if len(df.columns) < 2:
            raise ValueError(
                f"Worksheet '{sheet_name}' must contain a time column "
                "and at least one data column."
            )

        # The first column is the time column.
        time_column = df.columns[0]

        # Select the first column after time that contains numeric data.
        # This avoids using categorical columns such as 'Es'.
        value_column = None
        for column in df.columns[1:]:
            numeric = pd.to_numeric(df[column], errors="coerce")
            if numeric.notna().any():
                value_column = column
                break

        if value_column is None:
            raise ValueError(
                f"Worksheet '{sheet_name}' does not contain a numeric data column."
            )

        times = []
        values = []

        for raw_time, raw_value in zip(df[time_column], df[value_column]):
            try:
                hour = self._time_to_decimal(raw_time)
                value = self._to_float(raw_value)

                if np.isfinite(hour) and np.isfinite(value):
                    times.append(hour)
                    values.append(value)

            except (TypeError, ValueError):
                # Headers, empty cells and invalid rows are ignored.
                continue

        if not times:
            raise ValueError(
                f"Worksheet '{sheet_name}' has no valid time/value rows."
            )

        times = np.asarray(times, dtype=float)
        values = np.asarray(values, dtype=float)

        order = np.argsort(times)
        return times[order], values[order]

    def _parse_csv_line(self, raw_line):
        line = raw_line.strip("\r\n")
        if not line.strip():
            return None
        fields = next(csv.reader([line], delimiter=";", quotechar='"'))
        return self._extract_first_and_last(fields)

    def _parse_txt_line(self, raw_line):
        line = raw_line.strip("\r\n")
        if not line.strip():
            return None
        fields = [field for field in re.split(r"[\t ]+", line.strip()) if field]
        return self._extract_first_and_last(fields)

    def _extract_first_and_last(self, fields):
        non_empty = [str(field).strip() for field in fields if str(field).strip()]
        if len(non_empty) < 2:
            return None
        try:
            return self._to_float(non_empty[0]), self._to_float(non_empty[-1])
        except (TypeError, ValueError):
            return None

    def filter_data(self, times, values):
        times = np.asarray(times, dtype=float)
        values = np.asarray(values, dtype=float)
        valid = (np.isfinite(times) & np.isfinite(values) &
                 (times >= self.start_hour) & (times <= self.end_hour))
        return times[valid], values[valid]

    def calculate_periodogram(self, times, values):
        times = np.asarray(times, dtype=float)
        values = np.asarray(values, dtype=float)
        if times.size < 3:
            raise ValueError("Not enough samples for Lomb-Scargle.")

        unique_times, inverse = np.unique(times, return_inverse=True)
        if unique_times.size != times.size:
            sums = np.zeros(unique_times.size, dtype=float)
            counts = np.zeros(unique_times.size, dtype=int)
            np.add.at(sums, inverse, values)
            np.add.at(counts, inverse, 1)
            times = unique_times
            values = sums / counts

        if times.size < 3:
            raise ValueError("Not enough unique timestamps for Lomb-Scargle.")

        span = float(np.max(times) - np.min(times))
        if span <= 0:
            raise ValueError("The selected data has no time span.")

        diffs = np.diff(np.sort(times))
        diffs = diffs[diffs > 0]
        if diffs.size == 0:
            raise ValueError("Unable to determine sampling interval.")

        cadence = float(np.median(diffs))
        minimum_frequency = 1.0 / span
        maximum_frequency = 0.5 / cadence
        if maximum_frequency <= minimum_frequency:
            maximum_frequency = minimum_frequency * 2.0

        model = LombScargle(times, values, center_data=True, fit_mean=True)
        frequency, power = model.autopower(
            minimum_frequency=minimum_frequency,
            maximum_frequency=maximum_frequency,
            samples_per_peak=10,
        )

        valid = np.isfinite(frequency) & np.isfinite(power) & (frequency > 0)
        frequency, power = frequency[valid], power[valid]
        if frequency.size == 0:
            raise ValueError("Lomb-Scargle did not produce valid frequencies.")

        period = 1.0 / frequency
        order = np.argsort(period)
        return period[order], power[order], frequency[order]

    def show_graph(self, bold, grid):
        plt.close("all")
        fig, ax = plt.subplots(figsize=(10, 6))

        plotted = 0

        for result in self.results.values():
            if result.get("error") is not None:
                continue

            ax.plot(
                result["period_hours"],
                result["power"],
                linewidth=1.2,
                label=result["label"]
            )

            plotted += 1

        if plotted == 0:
            plt.close(fig)

            errors = []
            for result in self.results.values():
                if result.get("error") is not None:
                    errors.append(
                        f'{result["label"]}: {result["error"]}'
                    )

            if errors:
                raise RuntimeError(
                    "No valid periodograms were generated.\n\n"
                    + "\n".join(errors)
                )

            raise RuntimeError("No valid periodograms were generated.")

        ax.set_title("Lomb-Scargle Periodogram")
        ax.set_xlabel("Period (hours)")
        ax.set_ylabel("Power")
        ax.grid(grid, alpha=0.3)
        if bold:
            ax.xaxis.label.set_weight('bold')
            ax.yaxis.label.set_weight('bold')
            ax.title.set_weight('bold')
            for label in ax.get_xticklabels() + ax.get_yticklabels():
                label.set_fontweight('bold')

        ax.legend()

        fig.tight_layout()

        plt.show()

    def get_export_data(self):
        exported = {}
        for path, result in self.results.items():
            if result.get("error") is not None:
                continue
            exported[path] = {
                "period_hours": result["period_hours"].tolist(),
                "frequency_per_hour": result["frequency_per_hour"].tolist(),
                "file": result["file"],
                "sheet": result.get("sheet"),
                "label": result["label"],
                "power": result["power"].tolist(),
            }
        return exported

    def get_errors(self):
        return {path: result["error"] for path, result in self.results.items() if result.get("error") is not None}

    def clear_graph(self):
        self.results = {}
