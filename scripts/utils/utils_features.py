import utils_time
import objects
import numpy as np

def past_price_symbol_periods(data_dic, symbol, periods, time, gap_epoch=objects.GAP_EPOCH):

	'''
	Returns the price of the symbol n "periods" before "time"
	'''

	past_time = time - (gap_epoch * periods)
	past_price = float(data_dic[past_time][symbol]['close'])

	return past_price


def avg_price_symbol_periods(data_dic, symbol, periods, time, gap_epoch=objects.GAP_EPOCH):

	'''
	Returns the average price of the symbol for the last n "periods" previous to "time"
	'''

	prices = []
	for i in range(1, periods+1):

		time_iteration = time - (gap_epoch * i)
		prices.append(float(data_dic[time_iteration][symbol]['close']))

	return sum(prices) / len(prices)

def avg_price_bistamp(data):

	'''
	Returns the average of close prices in data.
	This assumes each item in data is an interval of five min but the avg
		needed is for 10 min intervals (hence it drops the close price
		of 1 every 2 observations).
	'''

	close_prices = []
	for i, data_point in enumerate(data):

		if i % 2 == 1:
			close_prices.append(float(data_point['close']))

	return sum(prices) / len(prices)

def avg_price(data_dic, periods, time):

	'''
	estimates the avg price (close) for time over the last X periods
	'''

	summation = 0
	n = 0

	for i in range(0, periods):

		past_time = utils_time.past_time(time, i)
		try:
			past_price = data_dic[past_time]['price_close']
			summation += past_price
			n += 1
		except KeyError:
			continue

	return summation / n

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

def is_valley(data_dic, time, both_sides= False, n=objects.VALLEY_PERIODS, gap=objects.PERIOD_DATA_MIN, margin=objects.MARGIN):

	'''
	Detects if a time is a valley with this rule:
	- the price for this time is the lowest in n periods before and after
	- at least one of the prices in n periods after is higher than the
		time price by a rate of (1 + margin)
	'''

	# Checking all times are in data_dic:
	for i in range(1, n + 1):
		future_time = utils_time.future_time(time, i, gap)
		if future_time not in data_dic:
			return np.nan

		if both_sides:
			past_time = utils_time.past_time(time, i, gap)
			if past_time not in data_dic:
				return np.nan
	
	current_price = data_dic[time]['price_close']

	for i in range(1, n + 1):

		if both_sides:
			# Checking periods before:
			past_time = utils_time.past_time(time, i, gap)
			past_price = data_dic[past_time]['price_close']
			if past_price < current_price:
				return 0
		
		# Checking periods after:
		future_time = utils_time.future_time(time, i, gap)
		future_price = data_dic[future_time]['price_close']
		if future_price < current_price:
			return 0
		if future_price > current_price * (1 + margin):
			return 1

	# if no price was lower or higher enough
	return 0

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

def max_price_is_open_fn(data_dic, time):

	try:
		max_price = data_dic[time]['price_high']
		open_price = data_dic[time]['price_open']
		if open_price == max_price:
			return 1
		else:
			return 0
	except KeyError:
		return np.nan

def min_price_is_open_fn(data_dic, time):

	try:
		min_price = data_dic[time]['price_low']
		open_price = data_dic[time]['price_open']
		if open_price == min_price:
			return 1
		else:
			return 0
	except KeyError:
		return np.nan

def max_price_is_close_fn(data_dic, time):

	try:
		max_price = data_dic[time]['price_high']
		close_price = data_dic[time]['price_close']
		if close_price == max_price:
			return 1
		else:
			return 0
	except KeyError:
		return np.nan

def min_price_is_close_fn(data_dic, time):

	try:
		min_price = data_dic[time]['price_low']
		close_price = data_dic[time]['price_close']
		if close_price == min_price:
			return 1
		else:
			return 0
	except KeyError:
		return np.nan

def price_range_oc(data_dic, time):

	try:
		price_open = data_dic[time]['price_open']
		price_close = data_dic[time]['price_close']
		return price_close - price_open
	except KeyError:
		return np.nan

def price_range_hl(data_dic, time):

	try:
		price_high = data_dic[time]['price_high']
		price_low = data_dic[time]['price_low']
		return price_high - price_low
	except KeyError:
		return np.nan

def price_range_oc_increase(data_dic, time):

	'''
	Open-close price range increased in time,
	with respect of the previous time
	'''

	previous_time = utils_time.past_time(time, 1)
	price_range_now = price_range_oc(data_dic, time)
	price_range_previous = price_range_oc(data_dic, previous_time)

	if np.isnan(price_range_now) or np.isnan(price_range_previous):
		return np.nan
	elif price_range_now > price_range_previous:
		return 1
	else:
		return 0

def price_range_hl_increase(data_dic, time):

	'''
	High-low price range increased in time,
	with respect of the previous time
	'''

	previous_time = utils_time.past_time(time, 1)
	price_range_now = price_range_hl(data_dic, time)
	price_range_previous = price_range_hl(data_dic, previous_time)

	if np.isnan(price_range_now) or np.isnan(price_range_previous):
		return np.nan
	elif price_range_now > price_range_previous:
		return 1
	else:
		return 0

def x_is_within_gap(x, y, gap):

	'''
	x is within y * (1 +- gap) 
	'''

	lower = y * (1 - gap)
	upper = y * (1 + gap)
	if x > lower and x < upper:
		return 1
	else:
		return 0

def feature_diff(data_dic, time, feature):

	'''
	Difference in the feature for time with respect of previous time
	'''

	previous_time = utils_time.past_time(time, 1)
	try:
		current_value = data_dic[time][feature]
		previous_value = data_dic[previous_time][feature]
	except KeyError:
		return np.nan

	return current_value - previous_value

def avg_vol_per_trade(data_dic, time):

	volume = get_volume(data_dic, time)
	trades = get_trades(data_dic, time)

	return volume / trades

def feature_increased_all_n(data_dic, time, n):

	'''
	Price increased in all periods for the last n periods
	'''

	return None

def feature_decreased_all_n(data_dic, time, n):

	'''
	Price decreased in all periods for the last n periods
	'''

	return None
