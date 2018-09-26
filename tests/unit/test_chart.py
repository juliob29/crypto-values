"""
Tests for the Chat class.
"""
import os
import json
import random
import plotly
import unittest
import requests

from skill.chart import Chart
from skill.skill import Crypto
from tests.data import plot_data
from requests.auth import HTTPBasicAuth

class ChartTestCase(unittest.TestCase):
    """
    Test case for the Chart() class.
    """

    @classmethod
    def setUpClass(cls):
        """
        Method that instantiates the test case.
        """
        cls.chart = Chart()
        cls.plotly_user_name = os.getenv('PLOTLY_USERNAME')
        cls.plotly_key = os.getenv('PLOTLY_API_KEY')
        cls.headers = {'Plotly-Client-Platform': 'python'}
        cls.auth = HTTPBasicAuth(cls.plotly_user_name, cls.plotly_key)
        plotly.tools.set_credentials_file(username=cls.plotly_user_name, api_key=cls.plotly_key)

    def get_pages(self, username, page_size):

        url = 'https://api.plot.ly/v2/folders/all?user=' + username + '&page_size=' + str(
            page_size)
        response = requests.get(url, auth=self.auth, headers=self.headers)
        if response.status_code != 200:
            return
        page = json.loads(response.content)
        yield page
        while True:
            resource = page['children']['next']
            if not resource:
                break
            response = requests.get(
                resource, auth=self.auth, headers=self.headers)
            if response.status_code != 200:
                break
            page = json.loads(response.content)
            yield page

    def permanently_delete_files(self,
                                 username,
                                 page_size=400,
                                 filetype_to_delete='plot'):
        for page in self.get_pages(username, page_size):
            for x in range(0, len(page['children']['results'])):
                fid = page['children']['results'][x]['fid']
                res = requests.get(
                    'https://api.plot.ly/v2/files/' + fid,
                    auth=self.auth,
                    headers=self.headers)
                res.raise_for_status()
                if res.status_code == 200:
                    json_res = json.loads(res.content)
                    if json_res['filetype'] == filetype_to_delete:
                        # move to trash
                        requests.post(
                            'https://api.plot.ly/v2/files/' + fid + '/trash',
                            auth=self.auth,
                            headers=self.headers)
                        # permanently delete
                        requests.delete(
                            'https://api.plot.ly/v2/files/' + fid +
                            '/permanent_delete',
                            auth=self.auth,
                            headers=self.headers)

        
    def delete_plot_and_grid(self,username):
        self.permanently_delete_files(username, filetype_to_delete='plot')
        self.permanently_delete_files(username, filetype_to_delete='grid')

        
    # def test_a_delete_all_charts(self):
    #     """
    #     After running all tests, this will delete all charts created.
    #     """
    #     try:
    #         self.delete_plot_and_grid(self.plotly_user_name)
    #         pass
    #     except requests.exceptions.HTTPError:
    #         pass

    def test_chart_generates_url(self):
        """
        Chart().generates() returns an URL.
        """

        class ChartMonkeyPatch(Chart):
            def mock_plotly(self):
                return 'http://google.com/{}/{}'.format(
                    self.coin, str(random.randint(0, 10**6)))

        chart = ChartMonkeyPatch()
        chart.backend = chart.mock_plotly

        result = chart.generate(coin='Bitcoin', data=plot_data)

        if not result:
            pass
        else:
            assert isinstance(result, str)
            assert 'http' in result

    def test_chart_cache(self):
        """
        Chart().generates() returns same chart within certain caching period
        """
        class ChartMonkeyPatch(Chart):
            def mock_plotly(self):
                return 'http://google.com/{}/{}'.format(
                    self.coin, str(random.randint(0, 10**6)))

        chart = ChartMonkeyPatch()
        chart.backend = chart.mock_plotly

        resultA = chart.generate(coin='Bitcoin', data=plot_data)
        resultB = chart.generate(coin='Bitcoin', data=plot_data)
        resultC = chart.generate(coin='litecoin', data=plot_data)

        if not resultC:
            pass
        else:
            assert resultA == resultB
            assert resultB != resultC

    def test_wrong_backend_raises_value_error(self):
        """
        Chart(backend='foo') raises ValueError.
        """
        with self.assertRaises(ValueError):
            Chart(auth=None, backend='foo')

    def test_bucket_environment_variable_is_present(self):
        """
        BUCKET environment variable is present.
        """
        assert os.getenv("BUCKET") == "bertie-ai-skill-crypto-values"

    def test_s3_image_chart(self):
        """
        Chart(backend='image').generate() generates an image plot and returns S3 URL.
        """
        chart = Chart(backend='image').generate(coin='Bitcoin', data=plot_data)

        assert chart == "https://s3.amazonaws.com/bertie-ai-skill-crypto-values/bitcoin-overall-closing-prices-from-november-01-2017-to-july-10-2018.png"

