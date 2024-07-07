import csv
import pandas as pd
import numpy as np

from typing import List, Dict
from itertools import combinations

from ent.trading_strategy import Strategy
from ent.utils import log, get_stock_name
from ent.base_ds import TradingDay, BaseConfig
from ent.visualizers import qf_visualize
from datetime import time

from ent.base_ds import Bar
from ent.base_mapper import BarMapper
from utils import to_datetime

from sklearn.cluster import DBSCAN


class VisualizingService:

    def __init__(self, sessions: Dict[str, TradingDay]):
        self.sessions = sessions

    def visualise_days(self, days_dates_list: List[str]):
        for day in days_dates_list:
            qf_visualize(self.sessions[day])


class StrategyService:

    def __init__(self, strategy: Strategy):
        self.strategy = strategy

    def test_strategy(self, trading_day: TradingDay):
        return self.strategy.get_results(trading_day)


class TradingDayService:

    @staticmethod
    def group_bars_by_days(bars: List[Bar], stock_name: str) -> Dict[str, TradingDay]:
        """
                Collection of trading days, where
                each day contains a list of bars.

                Example -> key:2022-03-30, value: TradingDay(list[bar1, bar2, bar3, ... barn])
            """

        # Group and clean data

        days = {}
        bar_dict = {}
        for bar in bars:
            bar_date = str(bar.date_time.date())
            if bar_date not in bar_dict:
                bar_dict[bar_date] = []
            bar_dict[bar_date].append(bar)

        for key, bars in bar_dict.items():
            if len(bars) == 79:
                days[key] = TradingDay(bars, stock_name)
            else:
                pass
                # log(f"Day {key} of stock: {stock_name} was skipped due "
                #     f"to wrong bars count - {len(bars)}. Required - 79")

        return days


class DataProviderService:
    mapper = BarMapper()
    start_time = time(9, 29)
    end_time = time(16, 1)
    five_min_bars = None

    def __init__(self, config: BaseConfig):
        self.config = config

    def read_5min_data(self):
        self.five_min_bars: List[Bar] = []
        with open(self.config.file_path, 'r', newline='') as csvfile:
            csv_reader = csv.reader(csvfile)
            next(csv_reader)

            for row in csv_reader:
                if self.start_time < to_datetime(row[0]).time() < self.end_time:
                    bar = self.mapper.list_to_bar(row)
                    if bar is not None:
                        self.five_min_bars.append(bar)
        return self

    def get_pandas_df(self) -> pd.DataFrame:
        df = BarMapper().bars_list_to_pandas_df_with_parsed_dates(self.five_min_bars)
        df['sma'] = df['open'].rolling(window=self.config.sma_window).mean()
        return df

    def get_data_as_trading_days(self) -> Dict[str, TradingDay]:
        stock_name = get_stock_name(self.config.file_path)
        return TradingDayService().group_bars_by_days(self.five_min_bars, stock_name)


class GridService:

    def __init__(self, type_vol, depth, coordinates_basis, data: pd.DataFrame):
        self.type_vol = type_vol
        self.depth = depth
        self.coordinates_basis = coordinates_basis
        self.data = data

    def _get_label(self, index):
        if index < 26:
            return chr(65 + index)
        else:
            return self._get_label(index // 26 - 1) + self._get_label(index % 26)

    def get(self) -> str:
        daily_data_full = self.data
        daily_data_for_coordinates = daily_data_full.head(self.depth)

        daily_low_depth = daily_data_for_coordinates[self.coordinates_basis].min()

        daily_high_full = daily_data_full['high'].max()
        daily_low_full = daily_data_full['low'].min()

        grid_height_full = int(np.ceil((daily_high_full - daily_low_full) / self.type_vol))
        grid_step_full = (daily_high_full - daily_low_full) / grid_height_full

        coordinates_str = []
        for i, (times, row) in enumerate(daily_data_for_coordinates.iterrows()):
            if i < self.depth:
                value_to_use = row[self.coordinates_basis] if not pd.isna(row[self.coordinates_basis]) else None
                if value_to_use is not None:
                    position = int((value_to_use - daily_low_depth) / grid_step_full)
                    y_label = self._get_label(position)
                    coord = f"{y_label}{i + 1}"
                    coordinates_str.append(coord)

        return '-'.join(coordinates_str)


class GroupByCorrelationService:

    @staticmethod
    def _convert_grid_to_numerical(coord_str):
        return [ord(c[0]) - ord('A') + 1 for c in coord_str.split('-')]

    @staticmethod
    def _find_correlated_pairs(data, threshold):
        correlated_pairs = {}
        for (index1, row1), (index2, row2) in combinations(data.iterrows(), 2):
            if len(row1['num_coords']) == len(row2['num_coords']):
                correlation = np.corrcoef(row1['num_coords'], row2['num_coords'])[0, 1]
                if correlation > threshold:
                    correlated_pairs[(index1, index2)] = correlation
        return correlated_pairs

    @staticmethod
    def _find_correlated_groups(pairs, threshold):
        groups = []

        for (idx1, idx2), corr in pairs.items():
            added = False
            for group in groups:
                if all(pairs.get((min(idx1, idx), max(idx1, idx)), 0) >= threshold and
                       pairs.get((min(idx2, idx), max(idx2, idx)), 0) >= threshold for idx in group):
                    group.update({idx1, idx2})
                    added = True
                    break

            if not added:
                groups.append({idx1, idx2})

        return groups

    def group(self, test_results: dict) -> pd.DataFrame:
        data = BarMapper.test_results_to_pandas_df(test_results)
        data['num_coords'] = data['grid'].apply(self._convert_grid_to_numerical)

        correlation_threshold = 0.85
        correlated_pairs = self._find_correlated_pairs(data, correlation_threshold)
        correlated_groups = self._find_correlated_groups(correlated_pairs, correlation_threshold)

        grouped_data = []
        for group in correlated_groups:
            group_data = data.loc[list(group)]
            avg_correlation = np.mean(
                [correlated_pairs[(min(idx1, idx2), max(idx1, idx2))] for idx1 in group for idx2 in group if
                 idx1 != idx2])
            for _, row in group_data.iterrows():
                key = (tuple(group), row['date'])
                if key not in grouped_data:
                    grouped_data.append({
                        'group': ' '.join(map(str, group)),
                        'stock_name': row['stock'],
                        'average_correlation': avg_correlation,
                        'date': row['date'],
                        'coordinates': row['grid'],
                        'side': row['opened_side'],
                        'result': row['revenue'],
                        'open': row['opened_price'],
                        'close': row['closed_price'],
                        'close_status': row['close_type'],
                        'open_time': row['opened_time'],
                        'close_time': row['closed_time']
                    })

        return pd.DataFrame(grouped_data)


class GroupByCorrelationService2:

    @staticmethod
    def _convert_grid_to_numerical(coord_str):
        return [ord(c[0]) - ord('A') + 1 for c in coord_str.split('-')]

    @staticmethod
    def _find_correlation_matrix(data):
        n = len(data)
        correlation_matrix = np.ones((n, n))
        for i, row1 in data.iterrows():
            for j, row2 in data.iterrows():
                if i < j:
                    correlation = np.corrcoef(row1['num_coords'], row2['num_coords'])[0, 1]
                    correlation_matrix[i, j] = correlation
                    correlation_matrix[j, i] = correlation
        return correlation_matrix

    def group(self, test_results: dict) -> pd.DataFrame:
        data = BarMapper.test_results_to_pandas_df(test_results)
        data['num_coords'] = data['grid'].apply(self._convert_grid_to_numerical)

        correlation_threshold = 0.85
        correlation_matrix = self._find_correlation_matrix(data)

        dbscan = DBSCAN(eps=1 - correlation_threshold, min_samples=2, metric='precomputed')
        labels = dbscan.fit_predict(1 - correlation_matrix)

        data['Group'] = labels

        grouped_data = []
        for group in data['Group'].unique():
            if group == -1:
                continue
            group_data = data[data['Group'] == group]
            avg_correlation = np.mean(
                [correlation_matrix[i, j] for i in group_data.index for j in group_data.index if i != j])
            for _, row in group_data.iterrows():
                grouped_data.append({
                    'group': 'Group ' + str(group),
                    'stock_name': row['stock'],
                    'average_correlation': avg_correlation,
                    'date': row['date'],
                    'coordinates': row['grid'],
                    'side': row['opened_side'],
                    'result': row['revenue'],
                    'open': row['opened_price'],
                    'close': row['closed_price'],
                    'close_status': row['close_type'],
                    'open_time': row['opened_time'],
                    'close_time': row['closed_time']
                })

        return pd.DataFrame(grouped_data)
