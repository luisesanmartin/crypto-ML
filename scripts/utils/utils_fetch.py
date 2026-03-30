import objects
import json
import requests
import utils_time
import utils_data
import utils_features

def get_data_bitstamp_from_to(
    start,
    end,
    crypto_symbol,
    step = 300
    ):
    
    '''
    Collects data from Bitstamp for a symbol.
    Times are in format: 'YYYY-MM-DD'.
    '''

    start_epoch = utils_time.time_in_epoch(start)
    end_epoch = utils_time.time_in_epoch(end)
    result = []
    time = start_epoch
    limit = 1000

    while time < end_epoch:

        result += get_data_bitstamp(step, crypto_symbol, time, limit)
        time += step * limit

    return result

def get_data_bitstamp(
    step = 300, # five minutes
    crypto_symbol=objects.SYMBOL_ID_BITSTAMP,
    start = None,
    limit = objects.PERIOD*2):

    '''
    gets OLHC data from Bitstamp
    '''

    request_url = objects.URL_BITSTAMP.format(crypto_symbol)
    parameters = {
        'step': step,
        'limit': limit
        }
    if start:
        parameters['start'] = start

    response = requests.get(request_url, params=parameters)
    data = json.loads(response.text)['data']['ohlc']

    return data