from typing import List

import seaborn as sns
import matplotlib.pyplot as plt
import cufflinks as cf
import plotly.offline as py
import plotly.io as pio

from ent.base_mapper import BarMapper
from ent.base_ds import Bar, TradingDay
from lightweight_charts import Chart


def qf_visualize(day: TradingDay, save=False):
    df = BarMapper().bars_list_to_pandas_df(day.bars)

    qf = cf.QuantFig(df, title=f"{day.stock_name} {day.date}", legend='top', name='GS')
    qf.add_sma([10, 20], width=2, color=['green', 'lightgreen'], legendgroup=True)
    qf.add_volume(column='volume')

    if save:
        fig = qf.iplot(asFigure=True)
        file_name = f"{day.stock_name}-{day.date}.png"
        pio.write_image(fig, file_name, width=1200, height=800)
    else:
        py.iplot(qf.iplot(asFigure=True))


def visualize_as_line_chart(bars: List[Bar]):
    plt.figure(figsize=(14, 5))
    sns.set_style("whitegrid")

    df = BarMapper().bars_list_to_pandas_df(bars)

    df_filled = df.fillna(method='ffill')
    sns.lineplot(data=df_filled, x='date_time', y='price_close', color='firebrick')

    plt.xlabel('Date')
    plt.ylabel('Close Price')
    plt.title('Close Price Over Time (with Netting)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def tw_visualize(day: TradingDay):
    chart = Chart(toolbox=True)
    chart.legend(visible=True, font_size=14, font_family='Arial')
    chart.topbar.textbox('symbol', day.stock_name)
    chart.topbar.switcher('timeframe', '5')
    df = BarMapper().bars_list_to_pandas_df_with_parsed_dates(day.bars)
    if not df.empty:
        chart.set(df)
    chart.show(block=True)
