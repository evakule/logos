from typing import Dict, Optional

from ent.base_ds import TradingDay, TestResults


class Strategy:

    def __init__(self, sl, depth):
        self.sl = sl
        self.depth = depth
        self.opened_price = 0.0
        self.opened_time = None
        self.side = ""
        self.opened = False
        self.closed_price = 0.0
        self.closed_time = None

    def get_results(self, day: TradingDay) -> Optional[TestResults]:
        self.reset()
        bars = day.bars
        start_bar = self.depth
        for i in range(start_bar, len(bars)):
            if not self.opened:
                self.opened_price = bars[i].price_open
                self.opened_time = bars[i].date_time
                self.opened = True
                if bars[0].price_open <= bars[i].price_close:
                    self.side = "LONG"
                else:
                    self.side = "SHORT"
            else:
                if self.side == "LONG" and bars[i].price_low < self.long_stop_loss_price():
                    self.closed_price = self.long_stop_loss_price()
                    self.closed_time = bars[i].date_time
                    return TestResults('stop_loss', f'-{self.sl}',
                                       self.side, day.stock_name, self.opened_price, self.opened_time,
                                       self.closed_price, self.closed_time)
                elif self.side == "SHORT" and bars[i].price_high > self.short_stop_loss_price():
                    self.closed_price = self.short_stop_loss_price()
                    self.closed_time = bars[i].date_time
                    return TestResults('stop_loss', f'-{self.sl}',
                                       self.side, day.stock_name, self.opened_price, self.opened_time,
                                       self.closed_price, self.closed_time)
                elif i == len(bars) - 1:
                    self.closed_price = bars[i].price_close
                    self.closed_time = bars[i].date_time
                    return TestResults('end_of_day', f'{self.calc_revenue(bars[i].price_close)}',
                                       self.side, day.stock_name, self.opened_price, self.opened_time,
                                       self.closed_price, self.closed_time)

    def reset(self):
        self.opened_price = 0.0
        self.side = ""
        self.opened = False
        self.opened_time = None
        self.closed_price = 0.0
        self.closed_time = None

    def long_stop_loss_price(self):
        return self.opened_price * (1 - self.sl / 100)

    def short_stop_loss_price(self):
        return self.opened_price * (1 + self.sl / 100)

    def calc_revenue(self, close):
        percentage_change = ((close - self.opened_price) / self.opened_price) * 100
        return round(abs(percentage_change), 2)
