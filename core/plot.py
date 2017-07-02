import plotly.plotly
import plotly.graph_objs as go
import pandas as pd
import plotly.offline as offline


class Plot:
    """
    Main plotting class
    """

    def __init__(self):
        pass

    @staticmethod
    def draw(df, df_trades):
        """
        Candle-stick plot
        """
        if df.empty:
            print('Plot: Empty dataframe, nothing to draw!')
            return

        df['date'] = pd.to_datetime(df['date'], unit='s')
        df_trades['date'] = pd.to_datetime(df_trades['date'], unit='s')
        print(df)
        plotly.offline.init_notebook_mode()

        trace = go.Candlestick(x=df.date,
                               open=df.open,
                               high=df.high,
                               low=df.low,
                               close=df.close)
        data = [trace]

        """
        # Save to file
        chart = offline.plot({'data': data,
                      'layout': {'title': 'Green Simulation Plot', 'autosize':True}},
                     filename='green-plot.html', validate=False, auto_open=True,
                     output_type='div', show_link='False', include_plotlyjs="False", link_text="")

        html_file = open("plot.html", "w")
        html_file.write(chart)
        html_file.close()
        """

        # Create buy/sell annotations
        annotations = []
        for index, row in df_trades.iterrows():
            d = dict(x=row['date'], y=row['close_price'], xref='x', yref='y', ax=0,
                     ay=-40 if row['close_price'] == 'buy' else 40,
                     showarrow=True, arrowhead=2, arrowsize=3, arrowwidth=2,
                     arrowcolor='red' if row['close_price'] == 'sell' else 'green',
                     bordercolor='#c7c7c7')
            annotations.append(d)

        layout = go.Layout(
            title='Simulation result',
            autosize=True,
            showlegend=True,
            annotations = annotations
        )

        # Auto-open html page
        offline.plot({'data': data, 'layout': layout},
                     auto_open=True,
                     image_filename='plot_image',
                     validate=False)
