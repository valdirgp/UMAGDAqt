'''from Model.GraphPage.GraphsModule import GraphsModule
import matplotlib.pyplot as plt
import re
import os
import csv
import numpy as np
import pandas as pd
from astropy.timeseries import LombScargle


class PeriodogramGraph(GraphsModule):
    """Lomb-Scargle periodogram for TXT, CSV and XLSX files.

    Lomb-Scargle is calculated internally in cycles/hour. The displayed X axis
    converts that frequency to cycles within a user-selected reference period,
    which defaults to 24 hours. Zero measurements are treated as missing data
    and are excluded from the Lomb-Scargle calculation.
    """

    def __init__(self, root, language):
        self.root = root
        self.lang = language
        self.files = []
        self.start_hour = 0.0
        self.end_hour = 24.0
        self.results = {}
        super().__init__(self.lang)

    def plot_periodogram(
        self,
        files=None,
        reference_period_hours=24.0,
        bold=False,
        grid=False,
    ):
        if files is not None:
            self.files = self._normalize_files(files)

        if not self.files:
            raise ValueError("No files were selected.")

        try:
            self.reference_period_hours = float(reference_period_hours)
        except (TypeError, ValueError):
            raise ValueError("Reference period must be a positive number of hours.")

        if not np.isfinite(self.reference_period_hours) or self.reference_period_hours <= 0:
            raise ValueError("Reference period must be a positive number of hours.")

        self.results = {}

        for path in self.files:
            extension = os.path.splitext(path)[1].lower()

            try:
                if extension in (".txt", ".csv"):
                    datasets = [(path, os.path.basename(path))]
                elif extension == ".xlsx":
                    excel = pd.ExcelFile(path)
                    datasets = [
                        (
                            f"{path}::{sheet}",
                            f"{os.path.basename(path)} - {sheet}",
                        )
                        for sheet in excel.sheet_names
                    ]
                else:
                    raise ValueError(
                        "Unsupported file format. Use TXT, CSV or XLSX files."
                    )

                for dataset_path, label in datasets:
                    try:
                        sheet = None

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

                        frequency_display, power, period, frequency_per_hour = (
                            self.calculate_periodogram(times, values)
                        )

                        self.results[dataset_path] = {
                            "file": path,
                            "sheet": sheet,
                            "label": label,
                            "time": times,
                            # Keep zero positions as NaN so they appear as
                            # blank gaps if the stored time series is plotted.
                            "value": np.where(values == 0, np.nan, values),
                            "frequency_per_hour": frequency_per_hour,
                            "frequency_in_reference_period": frequency_display,
                            "reference_period_hours": self.reference_period_hours,
                            "period_hours": period,
                            "power": power,
                            "error": None,
                        }

                    except Exception as exc:
                        self.results[dataset_path] = {
                            "file": path,
                            "sheet": (
                                dataset_path.split("::", 1)[1]
                                if extension == ".xlsx" and "::" in dataset_path
                                else None
                            ),
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
            second = (
                0
                if second_attr is None
                else (second_attr() if callable(second_attr) else second_attr)
            )

            return (
                float(hour)
                + float(minute) / 60.0
                + float(second) / 3600.0
            )

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
            sheets = pd.ExcelFile(path).sheet_names
            if not sheets:
                raise ValueError("The XLSX file does not contain any worksheets.")
            return self.read_xlsx_sheet(path, sheets[0])

        if extension not in (".txt", ".csv"):
            raise ValueError("Only TXT, CSV and XLSX files are supported.")

        times, values = [], []

        with open(
            path,
            "r",
            encoding="utf-8-sig",
            errors="replace",
            newline="",
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
        """Read one XLSX worksheet.

        Expected structure:
            - first column: time
            - first numeric column after time: measurement
            - later categorical/non-numeric columns are ignored
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

        time_column = df.columns[0]
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

        fields = [
            field
            for field in re.split(r"[\t ]+", line.strip())
            if field
        ]
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

        valid = (
            np.isfinite(times)
            & np.isfinite(values)
            & (times >= self.start_hour)
            & (times <= self.end_hour)
        )

        return times[valid], values[valid]

    def calculate_periodogram(self, times, values):
        """Calculate Lomb-Scargle and return display frequency, power, period,
        and the original frequency in cycles/hour.

        The displayed frequency is the number of cycles occurring during
        ``reference_period_hours``. Internally, Lomb-Scargle still uses
        cycles/hour. Zero-valued measurements are excluded before the
        calculation because they represent missing data.
        """
        times = np.asarray(times, dtype=float)
        values = np.asarray(values, dtype=float)

        if times.size < 3:
            raise ValueError("Not enough samples for Lomb-Scargle.")

        # Zero means missing/invalid data in this dataset. Do not let zero
        # values influence the Lomb-Scargle calculation. The original time
        # series can still retain those positions as NaN for other plots.
        valid_samples = (
            np.isfinite(times)
            & np.isfinite(values)
            & (values != 0)
        )
        times = times[valid_samples]
        values = values[valid_samples]

        if times.size < 3:
            raise ValueError(
                "At least 3 non-zero samples are required for Lomb-Scargle."
            )

        # Lomb-Scargle requires a unique time for each sample. If the source
        # contains repeated timestamps, average their measurements.
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

        # Make sure the samples are ordered in time.
        order = np.argsort(times)
        times = times[order]
        values = values[order]

        span = float(times[-1] - times[0])
        if span <= 0:
            raise ValueError("The selected data has no time span.")

        diffs = np.diff(times)
        diffs = diffs[np.isfinite(diffs) & (diffs > 0)]

        if diffs.size == 0:
            raise ValueError("Unable to determine sampling interval.")

        cadence = float(np.median(diffs))

        # Frequency is cycles/hour because time is supplied in hours.
        minimum_frequency = 1.0 / span
        nyquist_frequency = 0.5 / cadence
        maximum_frequency = nyquist_frequency

        if maximum_frequency <= minimum_frequency:
            raise ValueError(
                "The selected interval is too short for the detected sampling "
                "interval to define a useful frequency range."
            )

        model = LombScargle(
            times,
            values,
            center_data=True,
            fit_mean=True,
        )

        frequency, power = model.autopower(
            minimum_frequency=minimum_frequency,
            maximum_frequency=maximum_frequency,
            samples_per_peak=10,
        )

        valid = (
            np.isfinite(frequency)
            & np.isfinite(power)
            & (frequency > 0)
            & (power >= 0)
        )

        frequency = frequency[valid]
        power = power[valid]

        if frequency.size == 0:
            raise ValueError("Lomb-Scargle did not produce valid frequencies.")

        # Keep frequency ascending. Do NOT sort by period here: doing so
        # reverses the frequency direction and makes the graph misleading.
        order = np.argsort(frequency)
        frequency = frequency[order]
        power = power[order]

        period = 1.0 / frequency

        # Convert the Lomb-Scargle frequency (cycles/hour) into the number
        # of cycles occurring during the user-selected reference period.
        # Example: 0.25 cycles/hour * 24 hours = 6 cycles/24 hours.
        frequency_in_reference_period = frequency * self.reference_period_hours

        return frequency_in_reference_period, power, period, frequency

    def show_graph(self, bold, grid):
        plt.close("all")
        fig, ax = plt.subplots(figsize=(10, 6))

        plotted = 0

        for result in self.results.values():
            if result.get("error") is not None:
                continue

            ax.plot(
                result["frequency_in_reference_period"],
                result["power"],
                linewidth=1.2,
                label=result["label"],
            )
            plotted += 1

        if plotted == 0:
            plt.close(fig)

            errors = [
                f'{result["label"]}: {result["error"]}'
                for result in self.results.values()
                if result.get("error") is not None
            ]

            if errors:
                raise RuntimeError(
                    "No valid periodograms were generated.\n\n"
                    + "\n".join(errors)
                )

            raise RuntimeError("No valid periodograms were generated.")

        ax.set_title("Lomb-Scargle Periodogram")
        ax.set_xlabel(
            f"Frequency (cycles / {self.reference_period_hours:g} h)"
        )
        ax.set_ylabel("Power")
        ax.grid(grid, alpha=0.3)

        if bold:
            ax.xaxis.label.set_weight("bold")
            ax.yaxis.label.set_weight("bold")
            ax.title.set_weight("bold")

            for label in ax.get_xticklabels() + ax.get_yticklabels():
                label.set_fontweight("bold")

        ax.legend()
        fig.tight_layout()
        plt.show()

    def get_export_data(self):
        exported = {}

        for path, result in self.results.items():
            if result.get("error") is not None:
                continue

            exported[path] = {
                "frequency_per_hour": result["frequency_per_hour"].tolist(),
                "frequency_in_reference_period": result["frequency_in_reference_period"].tolist(),
                "reference_period_hours": result["reference_period_hours"],
                "period_hours": result["period_hours"].tolist(),
                "file": result["file"],
                "sheet": result.get("sheet"),
                "label": result["label"],
                "power": result["power"].tolist(),
            }

        return exported

    def get_errors(self):
        return {
            path: result["error"]
            for path, result in self.results.items()
            if result.get("error") is not None
        }

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
    """Lomb-Scargle periodogram for external TXT, CSV and XLSX files.

    The periodogram is calculated in frequency (cycles/hour), which is the
    natural independent variable of Lomb-Scargle. Period is still stored in
    the results for export/reference, but it is not used as the plot X axis.
    """

    def __init__(self, root, language):
        self.root = root
        self.lang = language
        self.files = []
        self.results = {}
        super().__init__(self.lang)

    def plot_periodogram(
        self,
        files=None,
        period_hours=24.0,
        bold=False,
        grid=False,
    ):
        if files is not None:
            self.files = self._normalize_files(files)

        self.period_hours = period_hours
        self.results = {}

        for path in self.files:
            extension = os.path.splitext(path)[1].lower()

            try:
                if extension in (".txt", ".csv"):
                    datasets = [(path, os.path.basename(path))]
                elif extension == ".xlsx":
                    excel = pd.ExcelFile(path)
                    datasets = [
                        (
                            f"{path}::{sheet}",
                            f"{os.path.basename(path)} - {sheet}",
                        )
                        for sheet in excel.sheet_names
                    ]
                else:
                    raise ValueError(
                        "Unsupported file format. Use TXT, CSV or XLSX files."
                    )

                for dataset_path, label in datasets:
                    try:
                        sheet = None

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

                        (
                            frequency,
                            power,
                            period,
                            peak_periods,
                            peak_powers,
                        ) = self.calculate_periodogram(times, values)

                        self.results[dataset_path] = {
                            "file": path,
                            "sheet": sheet,
                            "label": label,
                            "time": times,
                            "value": values,
                            "frequency_per_hour": frequency,
                            "period_hours": period,
                            "peak_periods": peak_periods,
                            "peak_powers": peak_powers,
                            "power": power,
                            "error": None,
                        }

                    except Exception as exc:
                        self.results[dataset_path] = {
                            "file": path,
                            "sheet": (
                                dataset_path.split("::", 1)[1]
                                if extension == ".xlsx" and "::" in dataset_path
                                else None
                            ),
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
            second = (
                0
                if second_attr is None
                else (second_attr() if callable(second_attr) else second_attr)
            )

            return (
                float(hour)
                + float(minute) / 60.0
                + float(second) / 3600.0
            )

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
            sheets = pd.ExcelFile(path).sheet_names
            if not sheets:
                raise ValueError("The XLSX file does not contain any worksheets.")
            return self.read_xlsx_sheet(path, sheets[0])

        if extension not in (".txt", ".csv"):
            raise ValueError("Only TXT, CSV and XLSX files are supported.")

        times, values = [], []

        with open(
            path,
            "r",
            encoding="utf-8-sig",
            errors="replace",
            newline="",
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
        """Read one XLSX worksheet.

        Expected structure:
            - first column: time
            - first numeric column after time: measurement
            - later categorical/non-numeric columns are ignored
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

        time_column = df.columns[0]
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

        fields = [
            field
            for field in re.split(r"[\t ]+", line.strip())
            if field
        ]
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

        valid = (
            np.isfinite(times)
            & np.isfinite(values)
            & (values != 0)
        )

        return times[valid], values[valid]

    def calculate_periodogram(self, times, values):
        """Calculate Lomb-Scargle and return period in hours as the main axis.

        Lomb-Scargle is calculated internally in frequency (cycles/hour),
        because that is the natural variable of the algorithm.

        The result is converted to period:

            period_hours = 1 / frequency

        Therefore the final graph uses:
            X = period in hours
            Y = Lomb-Scargle power

        Local maxima are also detected so each detected periodicity can be
        represented by one peak instead of several neighboring samples.
        """
        times = np.asarray(times, dtype=float)
        values = np.asarray(values, dtype=float)

        if times.size < 3:
            raise ValueError("Not enough samples for Lomb-Scargle.")

        # Lomb-Scargle requires unique timestamps.
        # Repeated timestamps are averaged.
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

        order = np.argsort(times)
        times = times[order]
        values = values[order]

        span = float(times[-1] - times[0])
        if span <= 0:
            raise ValueError("The selected data has no time span.")

        diffs = np.diff(times)
        diffs = diffs[np.isfinite(diffs) & (diffs > 0)]

        if diffs.size == 0:
            raise ValueError("Unable to determine sampling interval.")

        cadence = float(np.median(diffs))

        # Time is in hours, therefore frequency is cycles/hour.
        minimum_frequency = 1.0 / span
        nyquist_frequency = 0.5 / cadence
        maximum_frequency = nyquist_frequency

        if maximum_frequency <= minimum_frequency:
            raise ValueError(
                "The selected interval is too short for the detected sampling "
                "interval to define a useful frequency range."
            )

        model = LombScargle(
            times,
            values,
            center_data=True,
            fit_mean=True,
        )

        frequency, power = model.autopower(
            minimum_frequency=minimum_frequency,
            maximum_frequency=maximum_frequency,
            samples_per_peak=10,
        )

        valid = (
            np.isfinite(frequency)
            & np.isfinite(power)
            & (frequency > 0)
            & (power >= 0)
        )

        frequency = frequency[valid]
        power = power[valid]

        if frequency.size == 0:
            raise ValueError("Lomb-Scargle did not produce valid frequencies.")

        # Convert frequency to period in hours.
        period = 1.0 / frequency

        valid = (
            np.isfinite(period)
            & np.isfinite(power)
            & (period > 0)
            & (period <= self.period_hours)
        )

        frequency = frequency[valid]
        power = power[valid]
        period = period[valid]

        if period.size == 0:
            raise ValueError(
                f"No periods between 0 and {self.period_hours} hours were produced."
            )

        # X axis must increase from 0 to 24 hours.
        order = np.argsort(period)
        frequency = frequency[order]
        power = power[order]
        period = period[order]

        # Detect local maxima.
        # Neighboring samples belonging to the same broad peak are
        # consolidated, so a peak around 8 h remains one periodicity.
        peaks = []

        if power.size >= 3:
            max_power = float(np.max(power))
            threshold = max_power * 0.10

            for index in range(1, power.size - 1):
                if (
                    power[index] >= power[index - 1]
                    and power[index] >= power[index + 1]
                    and power[index] >= threshold
                ):
                    peaks.append(index)

        consolidated_peaks = []

        for index in peaks:
            if not consolidated_peaks:
                consolidated_peaks.append(index)
                continue

            previous = consolidated_peaks[-1]

            if abs(period[index] - period[previous]) < 0.5:
                if power[index] > power[previous]:
                    consolidated_peaks[-1] = index
            else:
                consolidated_peaks.append(index)

        peak_periods = period[consolidated_peaks]
        peak_powers = power[consolidated_peaks]

        return (
            frequency,
            power,
            period,
            peak_periods,
            peak_powers,
        )

    '''def show_graph(self, bold, grid):
        plt.close("all")
        fig, ax = plt.subplots(figsize=(10, 6))

        plotted = 0

        for result in self.results.values():
            if result.get("error") is not None:
                continue

            p_raw = result["power"]
            
            # Aplica a fórmula Min-Max para esticar o vetor entre 0 e 1
            # Se o denominador for zero (sinal constante), mantém zero.
            p_min, p_max = np.min(p_raw), np.max(p_raw)
            p_stretched = (p_raw - p_min) / (p_max - p_min) if (p_max - p_min) != 0 else p_raw

            # Main periodogram:
            # X = period in hours
            # Y = power
            ax.plot(
                result["period_hours"],
                p_stretched,
                #result["power"],
                linewidth=1.2,
                label=result["label"],
            )

            plotted += 1

        if plotted == 0:
            plt.close(fig)

            errors = [
                f'{result["label"]}: {result["error"]}'
                for result in self.results.values()
                if result.get("error") is not None
            ]

            if errors:
                raise RuntimeError(
                    "No valid periodograms were generated.\n\n"
                    + "\n".join(errors)
                )

            raise RuntimeError("No valid periodograms were generated.")

        ax.set_title("Lomb-Scargle Periodogram")
        ax.set_xlabel("Period (hours)")
        ax.set_ylabel("Power (Normalized 0-1)")

        # Requested X axis: 0 to 24 hours.
        # These are detected periods, not the original sample times.
        ax.set_xlim(0, self.period_hours)

        ax.grid(grid, alpha=0.3)

        if bold:
            ax.xaxis.label.set_weight("bold")
            ax.yaxis.label.set_weight("bold")
            ax.title.set_weight("bold")

            for label in ax.get_xticklabels() + ax.get_yticklabels():
                label.set_fontweight("bold")

        ax.legend()
        fig.tight_layout()
        plt.show()'''

    def show_graph(self, bold, grid):
        plt.close("all")

        # Filtra apenas os resultados válidos (sem erro) para plotagem
        valid_results = [r for r in self.results.values() if r.get("error") is None]
        
        if not valid_results:
            errors = [
                f'{result["label"]}: {result["error"]}'
                for result in self.results.values()
                if result.get("error") is not None
            ]
            if errors:
                raise RuntimeError(
                    "No valid periodograms were generated.\n\n" + "\n".join(errors)
                )
            raise RuntimeError("No valid periodograms were generated.")

        num_plots = len(valid_results)

        # Cria uma janela única. A altura (figsize) aumenta dinamicamente (4.0 * número de subplots)
        fig, axes = plt.subplots(
            nrows=num_plots, 
            ncols=1, 
            figsize=(10, 3.5 * num_plots), 
            sharex=True  # Compartilha o eixo X entre todos os gráficos para ficar mais limpo
        )

        # Se houver apenas 1 plot, 'axes' não vem como array. Convertemos para lista para o loop funcionar sempre.
        if num_plots == 1:
            axes = [axes]

        for ax, result in zip(axes, valid_results):
            # Obtém e normaliza as potências (Opção 2 - Min-Max)
            p_raw = result["power"]
            p_min, p_max = np.min(p_raw), np.max(p_raw)
            p_stretched = (p_raw - p_min) / (p_max - p_min) if (p_max - p_min) != 0 else p_raw

            # Plota a curva no subplot atual
            ax.plot(
                result["period_hours"],
                p_stretched,
                linewidth=1.2,
                label=result["label"],
            )

            # Rótulos e Títulos por subplot
            sheet_title = f" (Sheet: {result['sheet']})" if result.get("sheet") else ""
            ax.set_ylabel("Power (Normalized 0-1)")
            ax.set_title(f"Lomb-Scargle Periodogram{sheet_title}", fontsize=11)

            # Limites e configuração de Ticks de 3 em 3 horas
            ax.set_xlim(0, self.period_hours)
            ticks = np.arange(0, self.period_hours + 1, 3)
            ax.set_xticks(ticks)

            # Configurações visuais (Grade e Negrito)
            ax.grid(grid, alpha=0.3)
            ax.legend(loc="upper right")

            if bold:
                ax.yaxis.label.set_weight("bold")
                ax.title.set_weight("bold")
                for label in ax.get_xticklabels() + ax.get_yticklabels():
                    label.set_fontweight("bold")

        # Insere o rótulo do eixo X apenas no último gráfico da pilha para evitar repetição visual
        axes[-1].set_xlabel("Period (hours)")
        if bold:
            axes[-1].xaxis.label.set_weight("bold")

        # Ajusta o espaçamento para os subplots não se sobreporem
        fig.tight_layout()
        plt.show()


    def get_export_data(self):
        exported = {}

        for path, result in self.results.items():
            if result.get("error") is not None:
                continue

            exported[path] = {
                "frequency_per_hour": result["frequency_per_hour"].tolist(),
                "period_hours": result["period_hours"].tolist(),
                "peak_periods": result.get(
                    "peak_periods", np.array([])
                ).tolist(),
                "peak_powers": result.get(
                    "peak_powers", np.array([])
                ).tolist(),
                "file": result["file"],
                "sheet": result.get("sheet"),
                "label": result["label"],
                "power": result["power"].tolist(),
            }

        return exported

    def get_errors(self):
        return {
            path: result["error"]
            for path, result in self.results.items()
            if result.get("error") is not None
        }

    def clear_graph(self):
        self.results = {}

'''from xml.parsers.expat import errors
from Model.GraphPage.GraphsModule import GraphsModule
import matplotlib.pyplot as plt
import re
import os
import csv
import numpy as np
import pandas as pd
from astropy.timeseries import LombScargle


class PeriodogramGraph(GraphsModule):
    """Lomb-Scargle periodogram for external TXT, CSV and XLSX files.

    The periodogram is calculated in frequency (cycles/hour), which is the
    natural independent variable of Lomb-Scargle. Period is still stored in
    the results for export/reference, but it is not used as the plot X axis.
    """

    def __init__(self, root, language):
        self.root = root
        self.lang = language
        self.files = []
        self.results = {}
        super().__init__(self.lang)

    def plot_periodogram(
        self,
        files=None,
        period_hours=24.0,
        bold=False,
        grid=False,
    ):
        if files is not None:
            self.files = self._normalize_files(files)

        self.period_hours = period_hours
        self.results = {}

        for path in self.files:
            extension = os.path.splitext(path)[1].lower()

            try:
                if extension in (".txt", ".csv"):
                    datasets = [(path, os.path.basename(path))]
                elif extension == ".xlsx":
                    excel = pd.ExcelFile(path)
                    datasets = [
                        (
                            f"{path}::{sheet}",
                            f"{os.path.basename(path)} - {sheet}",
                        )
                        for sheet in excel.sheet_names
                    ]
                else:
                    raise ValueError(
                        "Unsupported file format. Use TXT, CSV or XLSX files."
                    )

                for dataset_path, label in datasets:
                    try:
                        sheet = None

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

                        (
                            frequency,
                            power,
                            period,
                            peak_periods,
                            peak_powers,
                        ) = self.calculate_periodogram(times, values)

                        self.results[dataset_path] = {
                            "file": path,
                            "sheet": sheet,
                            "label": label,
                            "time": times,
                            "value": values,
                            "frequency_per_hour": frequency,
                            "period_hours": period,
                            "peak_periods": peak_periods,
                            "peak_powers": peak_powers,
                            "power": power,
                            "error": None,
                        }

                    except Exception as exc:
                        self.results[dataset_path] = {
                            "file": path,
                            "sheet": (
                                dataset_path.split("::", 1)[1]
                                if extension == ".xlsx" and "::" in dataset_path
                                else None
                            ),
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
            second = (
                0
                if second_attr is None
                else (second_attr() if callable(second_attr) else second_attr)
            )

            return (
                float(hour)
                + float(minute) / 60.0
                + float(second) / 3600.0
            )

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
            sheets = pd.ExcelFile(path).sheet_names
            if not sheets:
                raise ValueError("The XLSX file does not contain any worksheets.")
            return self.read_xlsx_sheet(path, sheets[0])

        if extension not in (".txt", ".csv"):
            raise ValueError("Only TXT, CSV and XLSX files are supported.")

        times, values = [], []

        with open(
            path,
            "r",
            encoding="utf-8-sig",
            errors="replace",
            newline="",
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

        time_column = df.columns[0]
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

        fields = [
            field
            for field in re.split(r"[\t ]+", line.strip())
            if field
        ]
        return self._extract_first_and_last(fields)

    def _extract_first_and_last(self, fields):
        non_empty = [str(field).strip() for field in fields if str(field).strip()]

        if len(non_empty) < 2:
            return None

        try:
            return self._to_float(non_empty[0]), self._to_float(non_empty[-1])

        except (TypeError, ValueError):return None

    def filter_data(self, times, values):
        times = np.asarray(times, dtype=float)
        values = np.asarray(values, dtype=float)
        # Correção da precedência de operadores adicionando parênteses em (values != 0)
        valid = (np.isfinite(times) & np.isfinite(values) & (values != 0))
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
        order = np.argsort(times)
        times = times[order]
        values = values[order]
        span = float(times[-1] - times[0])
        if span <= 0:
            raise ValueError("The selected data has no time span.")
        diffs = np.diff(times)
        diffs = diffs[np.isfinite(diffs) & (diffs > 0)]
        if diffs.size == 0:
            raise ValueError("Unable to determine sampling interval.")
        cadence = float(np.median(diffs))
        minimum_frequency = 1.0 / span
        nyquist_frequency = 0.5 / cadence
        maximum_frequency = nyquist_frequency
        if maximum_frequency <= minimum_frequency:
            raise ValueError("The selected interval is too short for the detected sampling ""interval to define a useful frequency range.")
        model = LombScargle(times, values, center_data=True, fit_mean=True,)
        frequency, power = model.autopower(minimum_frequency=minimum_frequency, maximum_frequency=maximum_frequency, samples_per_peak=10,)
        valid = (np.isfinite(frequency) & np.isfinite(power) & (frequency > 0) & (power >= 0))
        frequency = frequency[valid]
        power = power[valid]
        if frequency.size == 0:
            raise ValueError("Lomb-Scargle did not produce valid frequencies.")
        period = 1.0 / frequency
        valid = (np.isfinite(period) & np.isfinite(power) & (period > 0) & (period <= self.period_hours))
        frequency = frequency[valid]
        power = power[valid]
        period = period[valid]
        if period.size == 0:
            raise ValueError(f"No periods between 0 and {self.period_hours} hours were produced.")
        order = np.argsort(period)
        frequency = frequency[order]
        power = power[order]
        period = period[order]
        # Detecção de máximos locais baseada em índices / vizinhança na frequência (amostragem linear)
        peaks = []
        if power.size >= 3:
            max_power = float(np.max(power))
            threshold = max_power * 0.10
            for index in range(1, power.size - 1):
                if (power[index] >= power[index - 1] and power[index] >= power[index + 1] and power[index] >= threshold):
                    peaks.append(index)
        consolidated_peaks = []
        # Consolidação usando a amostragem linear do vetor de frequências nativo do Lomb-Scargle.
        # Evita distorções de escala que acontecem ao calcular distâncias no eixo de Períodos.
        for index in peaks:
            if not consolidated_peaks:
                consolidated_peaks.append(index)
                continue
            previous = consolidated_peaks[-1]
            # Mescla picos se eles estiverem muito próximos em termos de bins/índices de amostragem
            if abs(index - previous) <= 10:
                if power[index] > power[previous]:
                    consolidated_peaks[-1] = index
                else:
                    consolidated_peaks.append(index)
        peak_periods = period[consolidated_peaks]
        peak_powers = power[consolidated_peaks]
        return (frequency, power, period, peak_periods, peak_powers)

    def show_graph(self, bold, grid):
        plt.close("all")
        fig, ax = plt.subplots(figsize=(10, 6))
        plotted = 0
        for result in self.results.values():
            if result.get("error") is not None:
                continue
            ax.plot(result["period_hours"], result["power"], linewidth=1.2, label=result["label"],)
            peak_periods = result.get("peak_periods", np.array([]))
            peak_powers = result.get("peak_powers", np.array([]))
            if len(peak_periods) > 0:
                ax.scatter(peak_periods, peak_powers, s=35, zorder=3,)
            plotted += 1

            if plotted == 0:
                plt.close(fig)
                errors = [f'{result["label"]}: {result["error"]}'for result in self.results.values()if result.get("error") is not None]

                if errors:
                    raise RuntimeError("No valid periodograms were generated.\n\n"+ "\n".join(errors))
                raise RuntimeError("No valid periodograms were generated.")
            ax.set_title("Lomb-Scargle Periodogram")
            ax.set_xlabel("Period (hours)")
            ax.set_ylabel("Power")
            # Ajuste dinâmico do limite do eixo X para suportar as configurações do usuário
            ax.set_xlim(0, self.period_hours)
            ax.grid(grid, alpha=0.3)
            if bold:
                ax.xaxis.label.set_weight("bold")
                ax.yaxis.label.set_weight("bold")
                ax.title.set_weight("bold")
            for label in ax.get_xticklabels() + ax.get_yticklabels():
                label.set_fontweight("bold")
            ax.legend()
            fig.tight_layout()
            plt.show()

    def get_export_data(self):
        exported = {}
        for path, result in self.results.items():
            if result.get("error") is not None:
                continue
            exported[path] = {
                "frequency_per_hour": result["frequency_per_hour"].tolist(),
                "period_hours": result["period_hours"].tolist(),
                "peak_periods": result.get("peak_periods", np.array([])).tolist(),
                "peak_powers": result.get("peak_powers", np.array([])).tolist(),
                "file": result["file"],
                "sheet": result.get("sheet"),
                "label": result["label"],
                "power": result["power"].tolist(),
            }
        return exported

    def get_errors(self):
        return {path: result["error"] for path, result in self.results.items() if result.get("error") is not None}

    def clear_graph(self):
        self.results = {}'''