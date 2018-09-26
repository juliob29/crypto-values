"""
Skill can find cryptocurrencies in text, and give their current listings.
"""
import re
import os
import time 
import gensim
import schedule
import plotly
import plotly.plotly as py

from isoweek import Week
from sanic.log import logger
from memoize import Memoizer
from skill.chart import Chart
from nltk.corpus import wordnet as wn
from datetime import datetime, timedelta
from skill.coinmarketcap import CoinMarketCap

store = {}
cached = Memoizer(store)


class Crypto:
    """
    This classes uses the CoinMarketCap library, along with a 
    regex search, to search for cryptocurrencies in a body
    of text, and output its current listing price in 
    the overall market.

    Parameters
    ----------
    model_path: str, default None
        Location of model to load. If left as None,
        this class will attempt to load the latest
        available model.

    related: bool, default False
        If the class should load the word2vec model
        for computing similarity statistics between
        currencies.

    charting_backend: str, default 'plotly'
        The charting backend to instantiate the Chart()
        class with. It can be either 'plotly' or 'image'

    """

    def __init__(self, charting_backend='plotly'):


        self.__initialize_variables()
        self.chart = Chart(backend=charting_backend)


    def __initialize_variables(self):
        """
        Restricts currencies to only currencies without a definition in WordNet.
        Returns
        -------
        self.currencies,self.symbols,self.website_slugs
            These variables contain the name, symbols, and website_slugs.
        """


        coins = CoinMarketCap.listings()
        currencies = [currency['name'] for currency in coins]
        # symbols = [currency['symbol']for currency in coins]
        coin_removal = []
        undesirable_coins = ['Crypto', 'ICOS', 'Naviaddress', 'B2BX']

        for i, currency in enumerate(currencies):
            if wn.synsets(currency) or currency in undesirable_coins:
                coin_removal.append(i)

        for index in sorted(coin_removal, reverse=True):
            del coins[index]

        self.coins = coins
        self.currencies = [currency['name'] for currency in coins]
        self.symbols = [currency['symbol'] for currency in coins]
        self.website_slugs = [currency['website_slug'] for currency in coins]
        self.coin_market_cap = CoinMarketCap()

    def _collect_coin_data(self,
                            coin,
                            start=(datetime.now() - timedelta(days=90)).strftime('%Y%m%d'),
                            dates_as_strings=True):
        """
        Simple method for collecting cryptocurrency data
        using CoinMarketCap().historic() and for parsing
        that data into the format expected by the
        Chart() class.
        Parameters
        ----------
        coin: str
            ID that identifies a unique cryptocurrency in
            CoinMarketCap.
        start: str, default datetime.now() - timedelta(days=90)
            String with a date value with ISO formatting.
        Returns
        -------
        plot_data: dict
            Dictionary with two keys: `date` and `close`.
            These keys contain lists of the dates and
            values for each cryptocurrency.
        """
        series = self.coin_market_cap.historic(coin, start=start)
        plot_data = {'date': [], 'close': []}
        for record in series:

            if dates_as_strings:
                date = record['date']
            else:
                date = datetime.strptime(record['date'], '%Y-%m-%d')

            plot_data['date'].append(date)
            plot_data['close'].append(record['close'])

        return plot_data

    @cached(max_age=60 * 60 * 10)
    def regex_crypto_currency_finder(self, string):
        '''
        This uses a regex to find a given currency, and place it in a list. 
        The list then places its results in the results dictionary. 
        This is done for regular currencies, its plurals, and its' symbols.
        Parameters
        ----------
        text: str
            Textual content to summarize.
        Returns
        -------
        result: Array of Objects
            Contains currency detected, its location, and the original sentence.
        '''

        results = []
        matches = {}
        caught_coin = []
        logger.info('Running regex on input')

        for i, currency in enumerate(self.currencies):
            regex = r"\b{}\b".format(currency)
            pattern = list(re.finditer(regex, string, re.I | re.M))

            count = 0
            # SINGULAR
            for match in pattern:
                if count == 0:
                    results.append({
                        "sentence": string,
                        "cryptocurrency": self.website_slugs[i],
                        "name": self.currencies[i],
                        "findings": [{
                            "name_start": match.start(),
                            "name_end": match.end()
                        }]
                    })
                    count = count + 1
                else:
                    matches.update({'name_start': match.start()})
                    matches.update({'name_end': match.end()})
                    for result in results:
                        if result['name'] == self.currencies[i]:
                            result['findings'].append(matches)
                        else:
                            pass
                    matches = {}

            regex_plural = r"\b{}s\b".format(currency)
            pattern_plural = list(
                re.finditer(regex_plural, string, re.I | re.M))

            #PLURAL
            for match in pattern_plural:
                if count == 0:
                    results.append({
                        "sentence": string,
                        "cryptocurrency": self.website_slugs[i],
                        "name": self.currencies[i],
                        "findings": [{
                            "name_start": match.start(),
                            "name_end": match.end()
                        }]
                    })
                    count = count + 1
                else:
                    matches.update({'name_start': match.start()})
                    matches.update({'name_end': match.end()})
                    for result in results:
                        if result['name'] == self.currencies[i]:
                            result['findings'].append(matches)
                        else:
                            pass
                    matches = {}

            if count > 0:
                caught_coin.append(i)
            else:
                pass
            count = 0

        count = 0
        #SYMBOL

        for i, symbol in enumerate(self.symbols):
            regex_symbol = r"\b{}\b".format(symbol)
            pattern_symbol = list(re.finditer(regex_symbol, string))

            for match in pattern_symbol:
                if count == 0 and i not in caught_coin:
                    results.append({
                        "sentence": string,
                        "cryptocurrency": self.website_slugs[i],
                        "name": self.currencies[i],
                        "findings": [{
                            "symbol_start": match.start(),
                            "symbol_end": match.end()
                        }]
                    })
                    count = count + 1
                elif i in caught_coin:
                    matches.update({'name_start': match.start()})
                    matches.update({'name_end': match.end()})

                    for result in results:
                        if result['name'] == self.currencies[i]:
                            result['findings'].append(matches)
                        else:
                            pass
                    matches = {}
            count = 0

        if not results:
            logger.info(
                'Did not find cryptocurrency in input. Returning empty.')
        else:
            logger.info(
                'Found {} cryptocurrencie(s). Limiting. Making chart(s).'.
                format(len(results)))

        return results

    @cached(max_age=60*60*10)
    def text(self, text, limit):
        """
        Uses text as an input. Regex search is called on text in order to return
        information about found cryptocurrencies
        Parameters
        ----------
        text: str
            Textual content to search for cryptocurrencies.
        limit: int 
            Limits regex output to value of int. Currencies with the most finds
            are the ones returned.
        Returns
        -------
        result: Array of Objects
            Contains currency detected, its location, its current close price,
            and a link to a plotly graph.
        """

        logger.info('Running skill. Input size: {} characters'.format(len(text)))

        findings = self.regex_crypto_currency_finder(text)

        sorted_findings = sorted(
            [{
                'coin': d['cryptocurrency'],
                'n': len(d['findings'])
            } for d in findings],
            key=lambda x: x['n'],
            reverse=True)
        top_coins = [x['coin'] for x in sorted_findings[:limit]]

        top_findings = [
            d for d in findings if d['cryptocurrency'] in top_coins
        ]

        results = []

        for finding in top_findings:

            logger.info("Running Chart with Plotly backend.")
            
            chart_url = self.chart.generate(
                coin=finding['name'],
                data=self._collect_coin_data(
                    coin=finding['cryptocurrency'], 
                    dates_as_strings=False))
            
            if not chart_url:

                logger.info("Running Chart with Image backend.")

                self.chart = Chart(backend='image')
                chart_url = self.chart.generate(
                    coin=finding['name'],
                    data=self._collect_coin_data(
                        coin=finding['cryptocurrency'], 
                        dates_as_strings=False))
            
            logger.info(f' → Chart generated: {chart_url}')
            
            related = []

            chart_title = self.chart.generate_title(
                coin=finding['name'],data=self._collect_coin_data(
                    coin=finding['cryptocurrency'], dates_as_strings=False))

            try:
                related = self.comparison_results[finding['name'].lower()][:10]

                logger.info(related)
                for coin in related:
                    coin['url'] = self.__fetch_latest_post_url(coin['name'])
            except KeyError:
                related = []

            except AttributeError:
                pass
            
            results.append({
                'id': finding['cryptocurrency'],
                'name': finding['name'],
                'matches': finding['findings'],
                'prices': self._collect_coin_data(
                    coin=finding['cryptocurrency']),
                'chart': {
                    "url": chart_url,
                    "caption": chart_title,
                    "source": "CoinMarketCap.com"
                }
            })
                    
        return results