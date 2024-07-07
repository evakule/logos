from typing import List


class BaseConfig:
    def __init__(self,
                 file_path: str = None,
                 sma_window: int = None,
                 type_vol: float = None,
                 depth: int = None,
                 coordinates_basis: str = None,
                 stop_loss: float = None):
        self.file_path = file_path
        self.sma_window = sma_window
        self.type_vol = type_vol
        self.depth = depth
        self.coordinates_basis = coordinates_basis
        self.stop_loss = stop_loss

    @staticmethod
    def builder():
        return BaseConfig.Builder()

    class Builder:
        def __init__(self):
            self._file_path = None
            self._sma_window = None
            self._type_vol = None
            self._depth = None
            self._coordinates_basis = None
            self._stop_loss = None

        def with_file_path(self, file_path: str):
            self._file_path = file_path
            return self

        def with_sma_window(self, sma_window: int):
            self._sma_window = sma_window
            return self

        def with_type_vol(self, type_vol: float):
            self._type_vol = type_vol
            return self

        def with_depth(self, depth: int):
            self._depth = depth
            return self

        def with_coordinates_basis(self, coordinates_basis: str):
            self._coordinates_basis = coordinates_basis
            return self

        def with_stop_loss(self, stop_loss: str):
            self._stop_loss = stop_loss
            return self

        def build(self):
            return BaseConfig(
                file_path=self._file_path,
                sma_window=self._sma_window,
                type_vol=self._type_vol,
                depth=self._depth,
                coordinates_basis=self._coordinates_basis,
                stop_loss=self._stop_loss
            )


class Bar:

    def __init__(self,
                 date_time,
                 price_open,
                 price_high,
                 price_low,
                 price_close,
                 volume,
                 ts):
        self.date_time = date_time
        self.price_open = price_open
        self.price_high = price_high
        self.price_low = price_low
        self.price_close = price_close
        self.volume = volume if volume else 0
        self.ts = ts

    def __str__(self):
        return (f"Bar: "
                f"DateTime={self.date_time}, "
                f"Open={self.price_open}, "
                f"High={self.price_high}, "
                f"Low={self.price_low}, "
                f"Close={self.price_close}, "
                f"Volume={self.volume}, "
                f"Timestamp={self.ts}")


class TradingDay:

    def __init__(self, bars: List[Bar], stock_name):
        self.bars = bars
        self.date = bars[0].date_time.date()
        self.stock_name = stock_name

    def __str__(self):
        return "\n".join([f"Trading day={self.date}, "
                          f"Open={bar.price_open}, "
                          f"High={bar.price_high}, "
                          f"Low={bar.price_low}, "
                          f"Close={bar.price_close}, "
                          f"Volume={bar.volume}" for bar in self.bars])


class BacktestObject:

    def __init__(self,
                 date: str,
                 grid: str,
                 trade_test_result: dict):
        self.date = date
        self.grid = grid
        self.trade_test_result = trade_test_result

    def __str__(self):
        return (f"BacktestObject(date={self.date}, "
                f"grid={self.grid}, "
                f"trade_test_result={self.trade_test_result})")


class TestResults:

    def __init__(self, close_type, revenue, opened_side, stock, opened_price, opened_time, closed_price, closed_time):
        self.close_type = close_type
        self.revenue = revenue
        self.opened_side = opened_side
        self.stock = stock
        self.opened_price = opened_price
        self.opened_time = opened_time
        self.closed_price = closed_price
        self.closed_time = closed_time

    def __str__(self):
        return (f"TestResults(close_type={self.close_type},"
                f" revenue={self.revenue}, "
                f"opened_side={self.opened_side}, "
                f"stock={self.stock}, "
                f"opened_price={self.opened_price}, "
                f"opened_time={self.opened_time}, "
                f"close_price={self.closed_price}, "
                f"close_time={self.closed_time})")
