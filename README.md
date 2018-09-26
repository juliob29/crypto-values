# Crypto Values
![Coverage](https://img.shields.io/badge/coverage-93%25-green.svg?style=flat-square)

This Bertie.ai skill returns to a user a search result, showing all found 
Cryptocurrencies from the [CoinMarketCap](https://coinmarketcap.com/) source. After locating the Cryptocurrencies,
a list of values from the end of a market day is given, and this information is then
graphed on a Plotly link, that can be inserted to any written article. If Plotly is 
unavailable, the program outputs a S3 link that contains the image instead.

# Usage

The application is run with `python run.py`. There are no additional docker containers 
associated with this application. 

The environment variables required for this application are located in the .env 
file in the repository. They are required to run the application. 

They include: 

* `S3_KEY`: The Amazon S3 Bucket Key needed for the `image` backend of the `Chart` class.
* `S3_SECRET`: The Amazon S3 Secret Key needed for the `image` backend of the `Chart` class. 
* `BUCKET`: The Amazon S3 Bucket name needed for the `image` backend of the `Chart` class.
* `PLOTLY_USERNAME`: The username of the Plotly account for the `plotly` backend of the `Chart` class.
* `PLOTLY_API_KEY`: The Plotly API Key for the `plotly` backend of the `Chart` class. 
* `PLOTLY_TIMEOUT`: A integer value that determines how many seconds to wait for Plotly's request. After timer, it will default to `image` backend.
* `CHARTING_BACKEND`: An integer that determines which backend to use, either `plotly` or `image`.


### Endpoints
This application contains one relevant endpoint:

* `/detect`: which returns the found Cryptocurrencies in text, their location, close prices, and Plotly graph.

That endpoint takes the following parameters:

* `text`: text input.
* `limit`: integer input. (Default is 3)

All requests have to be made using `POST` and passing a JSON object with the key above.

### Example Response
The skill returns a response in the following format.

```json
{
    "success": true,
    "message": "Searched `text` data successfully.",
    "results": [
        {
            "id": "bitcoin",
            "name": "Bitcoin",
            "matches": [
                {
                    "name_start": 0,
                    "name_end": 7
                }
            ],
            "prices": {
                "date": [
                    "2018-05-23",
                    "2018-05-24",
                    "2018-05-25",
                    "2018-05-26",
                    "2018-05-27",
                    "2018-05-28",
                    "2018-05-29",
                    "2018-05-30",
                    "2018-05-31",
                    "2018-06-01",
                    "2018-06-02",
                    "2018-06-03",
                    "2018-06-04",
                    "2018-06-05",
                    "2018-06-06",
                    "2018-06-07",
                    "2018-06-08",
                    "2018-06-09",
                    "2018-06-10",
                    "2018-06-11",
                    "2018-06-12",
                    "2018-06-13",
                    "2018-06-14",
                    "2018-06-15",
                    "2018-06-16",
                    "2018-06-17",
                    "2018-06-18",
                    "2018-06-19",
                    "2018-06-20",
                    "2018-06-21",
                    "2018-06-22",
                    "2018-06-23",
                    "2018-06-24",
                    "2018-06-25",
                    "2018-06-26",
                    "2018-06-27",
                    "2018-06-28",
                    "2018-06-29",
                    "2018-06-30",
                    "2018-07-01",
                    "2018-07-02",
                    "2018-07-03",
                    "2018-07-04",
                    "2018-07-05",
                    "2018-07-06",
                    "2018-07-07",
                    "2018-07-08",
                    "2018-07-09",
                    "2018-07-10",
                    "2018-07-11",
                    "2018-07-12",
                    "2018-07-13",
                    "2018-07-14",
                    "2018-07-15",
                    "2018-07-16",
                    "2018-07-17",
                    "2018-07-18",
                    "2018-07-19",
                    "2018-07-20",
                    "2018-07-21",
                    "2018-07-22",
                    "2018-07-23",
                    "2018-07-24",
                    "2018-07-25",
                    "2018-07-26",
                    "2018-07-27",
                    "2018-07-28",
                    "2018-07-29",
                    "2018-07-30",
                    "2018-07-31",
                    "2018-08-01",
                    "2018-08-02",
                    "2018-08-03",
                    "2018-08-04",
                    "2018-08-05",
                    "2018-08-06",
                    "2018-08-07",
                    "2018-08-08",
                    "2018-08-09",
                    "2018-08-10",
                    "2018-08-11",
                    "2018-08-12",
                    "2018-08-13",
                    "2018-08-14",
                    "2018-08-15",
                    "2018-08-16",
                    "2018-08-17",
                    "2018-08-18",
                    "2018-08-19",
                    "2018-08-20"
                ],
                "close": [
                    7557.82,
                    7587.34,
                    7480.14,
                    7355.88,
                    7368.22,
                    7135.99,
                    7472.59,
                    7406.52,
                    7494.17,
                    7541.45,
                    7643.45,
                    7720.25,
                    7514.47,
                    7633.76,
                    7653.98,
                    7678.24,
                    7624.92,
                    7531.98,
                    6786.02,
                    6906.92,
                    6582.36,
                    6349.9,
                    6675.35,
                    6456.58,
                    6550.16,
                    6499.27,
                    6734.82,
                    6769.94,
                    6776.55,
                    6729.74,
                    6083.69,
                    6162.48,
                    6173.23,
                    6249.18,
                    6093.67,
                    6157.13,
                    5903.44,
                    6218.3,
                    6404,
                    6385.82,
                    6614.18,
                    6529.59,
                    6597.55,
                    6639.14,
                    6673.5,
                    6856.93,
                    6773.88,
                    6741.75,
                    6329.95,
                    6394.71,
                    6228.81,
                    6238.05,
                    6276.12,
                    6359.64,
                    6741.75,
                    7321.04,
                    7370.78,
                    7466.86,
                    7354.13,
                    7419.29,
                    7418.49,
                    7711.11,
                    8424.27,
                    8181.39,
                    7951.58,
                    8165.01,
                    8192.15,
                    8218.46,
                    8180.48,
                    7780.44,
                    7624.91,
                    7567.15,
                    7434.39,
                    7032.85,
                    7068.48,
                    6951.8,
                    6753.12,
                    6305.8,
                    6568.23,
                    6184.71,
                    6295.73,
                    6322.69,
                    6297.57,
                    6199.71,
                    6308.52,
                    6334.73,
                    6580.63,
                    6423.76,
                    6506.07,
                    6308.53
                ]
            },
            "chart": {
                "url": "https://s3.amazonaws.com/bertie-ai-skill-crypto-values/bitcoin-overall-closing-prices-from-may-23-2018-to-august-20-2018.png",
                "caption": "Bitcoin Closing Prices from May 23, 2018 to August 20, 2018",
                "source": "CoinMarketCap.com"
            }
        }
    ]
}
```
