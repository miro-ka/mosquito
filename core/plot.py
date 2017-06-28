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
    def draw(df):
        if df.empty:
            print('Plot: Empty dataframe, nothing to draw!')
            return

        print(df)

        df['date'] = pd.to_datetime(df['date'], unit='s')
        #print(df)
        plotly.offline.init_notebook_mode()

        trace = go.Candlestick(x=df.date,
                               open=df.open,
                               high=df.high,
                               low=df.low,
                               close=df.close)
        data = [trace]

        """
        # Default
        def plot(figure_or_data, show_link=True, link_text='Export to plot.ly',
         validate=True, output_type='file', include_plotlyjs=True,
         filename='temp-plot.html', auto_open=True, image=None,
         image_filename='plot_image', image_width=800, image_height=600,
         config=None):
       """

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

        # Auto-open html page
        offline.plot({'data': data,
                      'layout': {'title': 'Simulation result', 'autosize': True}},
                     auto_open=True, image_filename='plot_image',  validate=False)
