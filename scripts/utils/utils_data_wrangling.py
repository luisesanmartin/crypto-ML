from sklearn import preprocessing
import utils_time
import objects
import numpy as np

def make_data_dic(data):

    '''
    Transforms the JSON data to a dictionary
    with period end as key
    '''

    data_dic = {}

    for data_point in data:

    	key = data_point['time_period_end'].split('.')[0]
    	data_dic[key] = data_point

    return data_dic

def price_increased(data_dic, time):

	'''
	Price increased by the end of "time" for that observation
	'''

	try:
		price_open = data_dic[time]['price_open']
		price_close = data_dic[time]['price_close']
	except KeyError:
		return np.nan

	if price_close > price_open:
		return 1
	else:
		return 0

def price_increased_next(data_dic, time, n, gap=objects.PERIOD_DATA_MIN):

	future_time = utils_time.future_time(time, n, gap)
	increased = price_increased(data_dic, future_time)

	return increased

def attribute_increased_for_time(data_dic, time, attribute, gap=objects.PERIOD_DATA_MIN):

	'''
	Attribute increased for 'time' with respect of its previous observation
	'''

	previous_time = utils_time.past_time(time, 1, gap)
	
	try:
		attribute_now = data_dic[time][attribute]
		attribute_past = data_dic[previous_time][attribute]
	except KeyError:
		return np.nan

	if attribute_now > attribute_past:
		return 1
	else:
		return 0

def volume_increased_past(data_dic, time, n, gap=objects.PERIOD_DATA_MIN):

	'''
	Volume increased n times ago with respect of its previous (n-1) observation
	'''

	initial_time = utils_time.past_time(time, n, gap)
	result = attribute_increased_for_time(data_dic, initial_time, 'volume_traded', gap)

	return result

def trades_increased_past(data_dic, time, n, gap=objects.PERIOD_DATA_MIN):

	'''
	Trades increased n times ago with respect of its previous (n-1) observation
	'''

	initial_time = utils_time.past_time(time, n, gap)
	result = attribute_increased_for_time(data_dic, initial_time, 'trades_count', gap)

	return result

def fit_standardizer(vector):

	array = np.array(vector).reshape(-1, 1)
	standardizer = preprocessing.StandardScaler().fit(array)

	return standardizer

def standardize(vector, standardizer):

	array = np.array(vector).reshape(-1, 1)
	result = standardizer.transform(array).flatten()

	return result

def get_price(data_dic, time):

	try:
		return data_dic[time]['price_close']
	except KeyError:
		return np.nan

def get_volume(data_dic, time):

	try:
		return data_dic[time]['volume_traded']
	except KeyError:
		return np.nan

def get_trades(data_dic, time):

	try:
		return data_dic[time]['trades_count']
	except KeyError:
		return np.nan

def max_price_is_open(data_dic, time):

	try:
		max_price = data_dic[time]['price_high']
		open_price = data_dic[time]['price_open']
		if open_price == max_price:
			return 1
		else:
			return 0
	except KeyError:
		return np.nan

def min_price_is_open(data_dic, time):

	try:
		min_price = data_dic[time]['price_low']
		open_price = data_dic[time]['price_open']
		if open_price == min_price:
			return 1
		else:
			return 0
	except KeyError:
		return np.nan

def max_price_is_close(data_dic, time):

	try:
		max_price = data_dic[time]['price_high']
		close_price = data_dic[time]['price_close']
		if close_price == max_price:
			return 1
		else:
			return 0
	except KeyError:
		return np.nan

def min_price_is_close(data_dic, time):

	try:
		min_price = data_dic[time]['price_low']
		close_price = data_dic[time]['price_close']
		if close_price == min_price:
			return 1
		else:
			return 0
	except KeyError:
		return np.nan