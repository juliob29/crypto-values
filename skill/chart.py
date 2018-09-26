"""
Classes and methods for creating Bertie-embedable charts.
"""
import io
import os
import tinys3
import plotly
import matplotlib
import plotly.plotly as py

from sanic.log import logger
from datetime import datetime

matplotlib.use('agg')

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import timeout_decorator as timeout


from slugify import slugify
from sanic.log import logger
from memoize import Memoizer
from plotly.graph_objs import *
from plotly.graph_objs import layout
from timeout_decorator.timeout_decorator import TimeoutError

store = {}
cached = Memoizer(store)


class Chart:
    """
    Interface for creating hosted charts using different
    backends. This class is instantiated with a backend 
    and generates a hosted chart using the `generate()`
    method. That method then returns an URL that is
    used for adding charts to Bertie.
    
    Parameters
    ----------
    backend: str, default 'plotly', {'plotly', 'image'}
        Name of the backend to use.
        
    auth: str or tuple
        Authentication for the required backend.
        For Plotly use (username, api_key).
    """

    def __init__(self, backend='plotly',
                 auth=(os.getenv('PLOTLY_USERNAME'), os.getenv('PLOTLY_API_KEY'))):

        self.backend = backend
        self.available_backends = {
            'plotly': self.__generate_plotly_graph,
            'image': self.__generate_matplotlib_image
        }

        if backend == 'plotly':
            plotly.tools.set_credentials_file(username=auth[0], api_key=auth[1])
            plotly.tools.set_config_file(world_readable=True, sharing='public')
        

        # NOTICE - The portion below was only useful when this project was in 
        # production! It is now my personal project! 


        # elif backend == 'image':
            # if not any([os.getenv('S3_KEY'), os.getenv('S3_SECRET')]):
            #     raise ValueError('The `image` backend needs two environment variables: ' + 
            #                      'S3_KEY and S3_SECRET.')

            # self.s3_bucket = os.getenv('BUCKET', 'bertie-ai-skill-crypto-values')
            # self.s3 = tinys3.Connection(
            #     access_key=os.getenv('S3_KEY'),
            #     secret_key=os.getenv('S3_SECRET'),
            #     default_bucket=self.s3_bucket)

        try:
            self.backend_method = self.available_backends[backend]
        except KeyError:
            raise ValueError(f'Backend `{backend} not available.')
            
            
    @timeout.timeout(int(os.getenv("PLOTLY_TIMEOUT",5)), use_signals=True)
    def __generate_plotly_graph(self):
        """
        Generates a plot using Plotly as a backend.
        Plotly will generate an online plot and then
        return that plot's URL. 
        Returns
        -------
        str
            URL for a given plot. This URL
            is what Bertie uses to create embeds.
        """
        plot_data = [
            Scatter(x=self.data['date'], y=self.data['close'], 
            mode='lines',
            line=dict(
                color='#2192ff',
                width = 3
            ))]
        
        start = min(self.data['date']).strftime('%B %d, %Y')
        stop = max(self.data['date']).strftime('%B %d, %Y')
        plot_layout = Layout(
            title=f'{self.coin} Closing Prices from {start} to {stop}',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=100,
            margin=layout.Margin(
                l=40,
                r=40,
                b=40,
                t=50,
                pad=4
            ),
            xaxis=dict(
                title='Source: CoinMarketCap (http://www.coinmarketcap.com)',
                titlefont=dict(
                        size=10,
                        color='#7f7f7f'
                )
            )
        )

        config = {'showLink':'testing config!'}
        fig = Figure(data=plot_data, layout=plot_layout)
        plot = py.plot(fig, auto_open=False, config=config)

        return plot
      
    @timeout.timeout(int(os.getenv("PLOTLY_TIMEOUT",3)), use_signals=True)  
    def __generate_matplotlib_image(self):
        """
        Generates a plot using Image as a backend.
        MatPlotLib will generate an offline plot and then
        upload it to the Amazon S3 bucket.
        Returns
        -------
        str
            URL for a given plot. This URL
            is what Bertie uses to create embeds.
        """
        
        
        start = min(self.data['date']).strftime('%B %d, %Y')
        stop = max(self.data['date']).strftime('%B %d, %Y')
        title = f'{self.coin} Overall Closing Prices from {start} to {stop}'

        file_name = slugify(title) + '.png'
        
        #
        # First, we create a MatplotLib image graph
        # and save it to root.
        #
        
    
            
            
        plt.figure(figsize=(10, 6), dpi=100)
        plt.plot(self.data['date'], self.data['close'])
        plt.gca().xaxis_date()
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %d, %Y'))
        plt.gca().yaxis.set_major_formatter(ticker.FormatStrFormatter("$%d"))
        plt.title(title)
        plt.xlabel("Dates")
        plt.ylabel("US Dollars")
        plt.xticks(rotation=10)
        plt.grid(linestyle="dotted")
        plt.savefig(file_name, transparent=True, dpi=100)
        
        
        
        

        
        return file_name

    @cached(max_age=60*60*10)
    def generate(self, coin, data):
        """
        Generates plot using class backend.
        
        Parameters
        ----------
        coin: str
            Coin name. This name will be used
            to generate the title of the plot.
        
        Returns
        -------
        str
            URL for the hosted plot. This URL
            can be used by Bertie to create an
            embeddable figure.
        """
        self.coin = coin
        self.data = data
        
        try:
            result = self.backend_method()
        except (plotly.exceptions.PlotlyRequestError, TimeoutError) as e:
            logger.error(f'Failed to generate chart with backend `{self.backend}`.')
            logger.error(f'Error: {e}')

            result = None

        return result

    @cached(max_age=60*60*10)
    def generate_title(self, coin, data):
        """
        Generates chart title. This is useful for creating
        image metadata elements.

        Parameters
        ----------
        coin: str
            Slug of cryptocurrency to use.

        data: dict
            Dictionary with at least one key: `date`.
            That key contains a list of strings representing
            ISO-formatted dates.

        Returns
        -------
        title: str
            Title of chart. 
        """
        self.coin = coin
        self.data = data 

        start = min(self.data['date']).strftime('%B %d, %Y')
        stop = max(self.data['date']).strftime('%B %d, %Y')
        title = f'{self.coin} Closing Prices from {start} to {stop}' 

        return title 