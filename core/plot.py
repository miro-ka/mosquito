import plotly.graph_objs as go
import pandas as pd
import plotly.offline as offline
from tzlocal import get_localzone


class Plot:
    """
    Main plotting class
    """

    def __init__(self):
        pass

    @staticmethod
    def draw(df, df_trades, pair, strategy_info):
        """
        Candle-stick plot
        """
        if df.empty:
            print('No data to plot!')
            return

        df = df[df['pair'] == pair]

        if df.empty:
            print('Plot: Empty dataframe, nothing to draw!')
            return

        pd.options.mode.chained_assignment = None

        df['date'] = pd.to_datetime(df['date'], unit='s', utc=True)
        df_trades['date'] = pd.to_datetime(df_trades['date'], unit='s', utc=True)
        local_tz = get_localzone()
        # Convert datetime to current time-zone
        df['date'] = df['date'].dt.tz_convert(local_tz)
        df = df.set_index(['date'])
        df_index = df.index.tz_localize(None)

        df_trades['date'] = df_trades['date'].dt.tz_convert(local_tz)
        df_trades = df_trades.set_index(['date'])

        # plotly.offline.init_notebook_mode()

        trace = go.Candlestick(x=df_index,
                               open=df.open,
                               high=df.high,
                               low=df.low,
                               close=df.close)
        data = [trace]

        # Create buy/sell annotations
        annotations = []
        for index, row in df_trades.iterrows():
            d = dict(x=index.tz_localize(None), y=row['close_price'], xref='x', yref='y', ax=0,
                     ay=40 if row['action'] == 'buy' else -40,
                     showarrow=True, arrowhead=2, arrowsize=3, arrowwidth=2,
                     arrowcolor='red' if row['action'] == 'sell' else 'green',
                     bordercolor='#c7c7c7')
            annotations.append(d)

        # Unpack the report string
        title = ''
        for item in strategy_info:
            s = str(item)
            title = title + '<BR>' + s

        layout = go.Layout(
            title=title,
            titlefont=dict(
                # family='Courier New, monospace',
                size=14,
                color='#606060'
            ),
            autosize=True,
            showlegend=False,
            annotations=annotations
        )

        # Auto-open html page
        offline.plot({'data': data, 'layout': layout},
                     auto_open=True,
                     image_filename='plot_image',
                     validate=False)
