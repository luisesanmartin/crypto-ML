import objects
import json
import requests
import utils_time
import utils_data
import utils_features

def get_api_key(text='API/key.txt'):

    with open(text) as file:
        key = file.read()

    return key

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

def get_data_bitstamp_symbols_now(
    step = objects.GAP_EPOCH,
    symbols = objects.BITSTAMP_SYMBOLS,
    limit = objects.PERIOD+1
    ):

    '''
    Return a dictionary with the current prices and average prices
    for the last limit-1 periods for all symbols
    '''

    all_data = {symbol: get_data_bitstamp(step=step, crypto_symbol=symbol, limit=limit) for symbol in symbols}
    data_dic = utils_data.make_data_dic_bitstamp(all_data)
    time = list(data_dic.keys())[-1]

    current_prices = {symbol: float(data_dic[time][symbol]['close']) for symbol in symbols}
    avg_prices = {symbol: utils_features.avg_price_symbol_periods(data_dic, symbol, limit-1, time) for symbol in symbols}

    return current_prices, avg_prices

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

def get_data_min(period=objects.PERIOD_DATA, crypto_symbol=objects.SYMBOL_ID):

    '''
    Retrieves data for a crypto, with a frequency of 'period'
    '''

    request_url = objects.URL.format(crypto_symbol)
    headers = {"X-CoinAPI-Key": get_api_key()}
    parameters = {'period_id': objects.PERIOD_DATA}

    response = requests.get(request_url, headers=headers, params=parameters)
    data = json.loads(response.text)

    return data

def get_data_max(n=objects.DATA_MAX, period=objects.PERIOD_DATA, crypto_symbol=objects.SYMBOL_ID):

    '''
    Retrieves data for a crypto, with a frequency of 'period'
    '''

    request_url = objects.URL.format(crypto_symbol)
    headers = {"X-CoinAPI-Key": get_api_key()}
    parameters = {
        'period_id': objects.PERIOD_DATA,
        'limit': n
    }

    response = requests.get(request_url, headers=headers, params=parameters)
    data = json.loads(response.text)

    return data