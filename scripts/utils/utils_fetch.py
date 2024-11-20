import objects
import json
import requests

def get_api_key(text='API/key.txt'):

    with open(text) as file:
        key = file.read()

    return key

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
        'period_id': period,
        'limit': n
    }

    response = requests.get(request_url, headers=headers, params=parameters)
    data = json.loads(response.text)

    return data

def get_data_with_limits(start, end, n=objects.DATA_MAX, period=objects.PERIOD_DATA, crypto_symbol=objects.SYMBOL_ID):

    '''
    Retrieves data for a crypto, with a frequency of 'period', from 'start' to 'end'
    '''

    request_url = objects.URL.format(crypto_symbol)
    headers = {"X-CoinAPI-Key": get_api_key()}
    parameters = {
        'period_id': period,
        'time_start': start,
        'time_end': end,
        'limit': n
    }

    response = requests.get(request_url, headers=headers, params=parameters)
    data = json.loads(response.text)

    return data