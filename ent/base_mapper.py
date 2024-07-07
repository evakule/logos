import pandas as pd

from ent.base_ds import Bar
from typing import List
from utils import to_datetime, to_float, to_int


class BarMapper:

    @staticmethod
    def list_to_bar(row: list) -> Bar:
        bar = Bar(to_datetime(row[0]),
                  to_float(row[3]),
                  to_float(row[4]),
                  to_float(row[5]),
                  to_float(row[6]),
                  to_int(row[7]),
                  to_datetime(row[0]).timestamp())

        if bar.price_low is not None:
            return bar

    @staticmethod
    def bars_list_to_pandas_df(bars: List[Bar]) -> pd.DataFrame:
        data = {
            'date_time': [bar.date_time for bar in bars],
            'open': [bar.price_open for bar in bars],
            'high': [bar.price_high for bar in bars],
            'low': [bar.price_low for bar in bars],
            'close': [bar.price_close for bar in bars],
            'volume': [bar.volume for bar in bars],
            'timestamp': [bar.ts for bar in bars],
        }
        df = pd.DataFrame(data)
        df['date_time'] = pd.to_datetime(df['date_time']).dt.strftime('%H:%M').astype(str)
        df.set_index('date_time', inplace=True)
        return df

    @staticmethod
    def bars_list_to_pandas_df_with_parsed_dates(bars: List[Bar]) -> pd.DataFrame:
        data = {
            'datetime': [bar.date_time for bar in bars],
            'open': [bar.price_open for bar in bars],
            'high': [bar.price_high for bar in bars],
            'low': [bar.price_low for bar in bars],
            'close': [bar.price_close for bar in bars],
            'volume': [bar.volume for bar in bars],
            'timestamp': [bar.ts for bar in bars],
        }
        df = pd.DataFrame(data)
        df['datetime'] = pd.to_datetime(df['datetime'])
        df.set_index('datetime', inplace=True)
        return df

    @staticmethod
    def test_results_to_pandas_df(test_results: dict) -> pd.DataFrame:
        # stock_name, date, Coordinates, Side, Result, Open--, Close--, Close Status, Open Time--, Close Time--
        data_list = []

        for date, backtest in test_results.items():
            row = {
                'date': backtest.date,
                'grid': backtest.grid,
                'close_type': backtest.trade_test_result.close_type,
                'revenue': backtest.trade_test_result.revenue,
                'opened_side': backtest.trade_test_result.opened_side,
                'stock': backtest.trade_test_result.stock,
                'opened_price': backtest.trade_test_result.opened_price,
                'opened_time': backtest.trade_test_result.opened_time,
                'closed_price': backtest.trade_test_result.closed_price,
                'closed_time': backtest.trade_test_result.closed_time
            }
            data_list.append(row)

        return pd.DataFrame(data_list)
