#import robin_stocks.robinhood as robinhood
#import robin_stocks.robinhood.orders as rh
import json
import hashlib
import hmac
import time
import requests
import uuid
import sys
from urllib.parse import urlencode
import objects
from email.message import EmailMessage
import smtplib

def bs_credentials():

    '''
    '''

    with open('API/credentials_bs.json') as f:
        login_info = json.load(f)

    api_key = login_info['key']
    secret = login_info['secret']

    return api_key, secret

def email_credentials():

    '''
    '''

    with open('API/email-credentials.json') as f:
        email = json.load(f)

    sender = email['sender']
    to = email['to']
    key = email['password']

    return sender, to, key

def send_email(message, subject, sender, to, key):

    '''
    '''

    # Message content
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = to
    msg.set_content(message)

    # Credendials and sending
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.login(sender, key)
    server.send_message(msg)
    server.quit()

    return True

def bs_sell_limit_order(amount, price, market_symbol, credentials=bs_credentials()):

    '''
    Checks account balance
    '''

    api_key = credentials[0]
    secret = credentials[1]
    secret = secret.encode('utf-8')

    # This part is taken from the online example
    timestamp = str(int(round(time.time() * 1000)))
    nonce = str(uuid.uuid4())
    content_type = 'application/x-www-form-urlencoded'
    payload = {
        'amount': amount,
        'price': price
    }
    url_path_query = '/api/v2/sell/{}/'.format(market_symbol)

    payload_string = urlencode(payload)

    message = 'BITSTAMP ' + api_key + \
        'POST' + \
        'www.bitstamp.net' + \
        url_path_query + \
        content_type + \
        nonce + \
        timestamp + \
        'v2' + \
        payload_string
    message = message.encode('utf-8')
    signature = hmac.new(secret, msg=message, digestmod=hashlib.sha256).hexdigest()
    headers = {
        'X-Auth': 'BITSTAMP ' + api_key,
        'X-Auth-Signature': signature,
        'X-Auth-Nonce': nonce,
        'X-Auth-Timestamp': timestamp,
        'X-Auth-Version': 'v2',
        'Content-Type': content_type
    }
    r = requests.post(
        f'https://www.bitstamp.net{url_path_query}',
        headers=headers,
        data=payload_string
    )

    return r

def bs_buy_limit_order(amount, price, market_symbol, credentials=bs_credentials()):

    '''
    Checks account balance
    '''

    api_key = credentials[0]
    secret = credentials[1]
    secret = secret.encode('utf-8')

    # This part is taken from the online example
    timestamp = str(int(round(time.time() * 1000)))
    nonce = str(uuid.uuid4())
    content_type = 'application/x-www-form-urlencoded'
    payload = {
        'amount': amount,
        'price': price
    }
    url_path_query = '/api/v2/buy/{}/'.format(market_symbol)

    payload_string = urlencode(payload)

    message = 'BITSTAMP ' + api_key + \
        'POST' + \
        'www.bitstamp.net' + \
        url_path_query + \
        content_type + \
        nonce + \
        timestamp + \
        'v2' + \
        payload_string
    message = message.encode('utf-8')
    signature = hmac.new(secret, msg=message, digestmod=hashlib.sha256).hexdigest()
    headers = {
        'X-Auth': 'BITSTAMP ' + api_key,
        'X-Auth-Signature': signature,
        'X-Auth-Nonce': nonce,
        'X-Auth-Timestamp': timestamp,
        'X-Auth-Version': 'v2',
        'Content-Type': content_type
    }
    r = requests.post(
        f'https://www.bitstamp.net{url_path_query}',
        headers=headers,
        data=payload_string
    )

    return r

def bs_sell_market_order(amount, market_symbol, credentials=bs_credentials()):

    '''
    Checks account balance
    '''

    api_key = credentials[0]
    secret = credentials[1]
    secret = secret.encode('utf-8')

    # This part is taken from the online example
    timestamp = str(int(round(time.time() * 1000)))
    nonce = str(uuid.uuid4())
    content_type = 'application/x-www-form-urlencoded'
    payload = {
        'amount': amount
    }
    url_path_query = '/api/v2/sell/market/{}/'.format(market_symbol)

    payload_string = urlencode(payload)

    message = 'BITSTAMP ' + api_key + \
        'POST' + \
        'www.bitstamp.net' + \
        url_path_query + \
        content_type + \
        nonce + \
        timestamp + \
        'v2' + \
        payload_string
    message = message.encode('utf-8')
    signature = hmac.new(secret, msg=message, digestmod=hashlib.sha256).hexdigest()
    headers = {
        'X-Auth': 'BITSTAMP ' + api_key,
        'X-Auth-Signature': signature,
        'X-Auth-Nonce': nonce,
        'X-Auth-Timestamp': timestamp,
        'X-Auth-Version': 'v2',
        'Content-Type': content_type
    }
    r = requests.post(
        f'https://www.bitstamp.net{url_path_query}',
        headers=headers,
        data=payload_string
    )

    return r

def bs_check_balance(currency, credentials=bs_credentials()):

    '''
    Checks account balance
    '''

    api_key = credentials[0]
    secret = credentials[1]
    secret = secret.encode('utf-8')

    # This part is taken from the online example
    timestamp = str(int(round(time.time() * 1000)))
    nonce = str(uuid.uuid4())
    content_type = 'application/x-www-form-urlencoded'
    payload = {'offset': '1'}
    url_path_query = '/api/v2/account_balances/{}/'.format(currency)

    payload_string = urlencode(payload)

    message = 'BITSTAMP ' + api_key + \
        'POST' + \
        'www.bitstamp.net' + \
        url_path_query + \
        content_type + \
        nonce + \
        timestamp + \
        'v2' + \
        payload_string
    message = message.encode('utf-8')
    signature = hmac.new(secret, msg=message, digestmod=hashlib.sha256).hexdigest()
    headers = {
        'X-Auth': 'BITSTAMP ' + api_key,
        'X-Auth-Signature': signature,
        'X-Auth-Nonce': nonce,
        'X-Auth-Timestamp': timestamp,
        'X-Auth-Version': 'v2',
        'Content-Type': content_type
    }
    r = requests.post(
        f'https://www.bitstamp.net{url_path_query}',
        headers=headers,
        data=payload_string
    )
    #return r
    if not r.status_code == 200:
        raise Exception('Status code not 200')

    string_to_sign = (nonce + timestamp + r.headers.get('Content-Type')).encode('utf-8') + r.content
    signature_check = hmac.new(secret, msg=string_to_sign, digestmod=hashlib.sha256).hexdigest()
    if not r.headers.get('X-Server-Auth-Signature') == signature_check:
        raise Exception('Signatures do not match')

    return r

def login():

    '''
    Logs in
    '''

    with open('API/credentials_rb.json') as f:
        login_info = json.load(f)

    login = robinhood.login(login_info['username'], login_info['password'])

    return login

def buy_crypto(crypto, usd_amount):

    '''
    Buys the specified amount of dollars of crypto
    '''

    order = rh.order_buy_crypto_by_price(crypto, usd_amount)

    return order

def buy_crypto_limit(crypto, usd_amount, limit_price):

    '''
    Buys the specified amount of dollars of crypto, with a limit price
    '''

    order = rh.order_buy_crypto_limit_by_price(crypto, usd_amount, limit_price)

    return order

def sell_crypto(crypto, crypto_amount):

    '''
    Sells the specified amount of crypto at the current price
    '''

    order = rh.order_sell_crypto_by_quantity(crypto, crypto_amount)

    return order

def sell_crypto_limit(crypto, crypto_amount, limit_price):

    '''
    Sells the specified amount of crypto with a limit price
    '''

    order = rh.order_sell_crypto_limit(crypto, crypto_amount, limit_price)

    return order
