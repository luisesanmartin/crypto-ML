from sklearn import preprocessing
from sklearn import model_selection
import utils_time
import utils_features
import objects
import numpy as np
import pickle
import torch
import pandas as pd

def make_data_dic(data):

    '''
    Transforms the JSON data to a dictionary
    with period end as key
    '''

    data_dic = {}

    for data_point in data:

    	try:
    		key = data_point['time_period_end'].split('.')[0]
    	except TypeError:
    		print("data_point:")
    		print(data_point)
    		raise TypeError
    	data_dic[key] = data_point

    return data_dic

def fit_standardizer(vector):

	array = np.array(vector).reshape(-1, 1)
	standardizer = preprocessing.StandardScaler().fit(array)

	return standardizer

def standardize(vector, standardizer):

	array = np.array(vector).reshape(-1, 1)
	result = standardizer.transform(array).flatten()

	return result

def make_x_predict(data_dic):

	'''
	Creates the complete data row for producing predictions
	'''

	data = make_x(data_dic)
	data = np.array(data).flatten()

	return data

def make_data_train_test(data_dic, cols=objects.COLS):

	# Variables needed only in training
	times = list(data_dic.keys())
	valleys = [utils_features.is_valley(data_dic, time) for time in times]

	# All other variables
	data = make_x(data_dic, for_prediction=False)
	data = [times, valleys] + data
	df = pd.DataFrame(dict(zip(cols, data)))

	# Removing obs with nan
	n1 = len(df)
	df = df.dropna(how='any')
	n2 = len(df)
	print('\tObservations: {}'.format(n2))
	print('\tKept {}% of initial obs after dropping columns with missings'.format(round(n2/n1*100)))

	df_train, df_test = model_selection.train_test_split(df, test_size=objects.TEST_SIZE)

	return df_train, df_test

def make_x(
	data_dic,
	standardizers_path='../models/standardizers/',
	binners_path = '../models/binners/',
	for_prediction=True
	):

	# ID variable: end time of period
	times = list(data_dic.keys())
	if for_prediction: # leave only the most recent time
		times = times[0:1]

	# Price increased in this observation
	inc_price = [utils_features.price_increased_next(data_dic, time, 0) for time in times]

	# Standardized close price
	close_prices = [data_dic[time]['price_close'] for time in times]
	if for_prediction:
		with open(standardizers_path+'standardizer_prices.pkl', 'rb') as f:
			standardizer = pickle.load(f)
	else:
		standardizer = fit_standardizer(close_prices)
		with open(standardizers_path+'standardizer_prices.pkl', 'wb') as f:
			pickle.dump(standardizer, f)
	close_prices_standardized = standardize(close_prices, standardizer)

	# Price increase in last X observations
	inc_price_last1 = [utils_features.price_increased_next(data_dic, time, -1) for time in times]
	inc_price_last2 = [utils_features.price_increased_next(data_dic, time, -2) for time in times]
	inc_price_last3 = [utils_features.price_increased_next(data_dic, time, -3) for time in times]
	inc_price_last4 = [utils_features.price_increased_next(data_dic, time, -4) for time in times]
	inc_price_last5 = [utils_features.price_increased_next(data_dic, time, -5) for time in times]
	inc_price_last6 = [utils_features.price_increased_next(data_dic, time, -6) for time in times]

	# Volume increased in this observation
	inc_vol = [utils_features.attribute_increased_for_time(data_dic, time, 'volume_traded') for time in times]

	# Standardized volume traded
	volumes = [data_dic[time]['volume_traded'] for time in times]
	if for_prediction:
		with open(standardizers_path+'standardizer_volumes.pkl', 'rb') as f:
			standardizer = pickle.load(f)
	else:
		standardizer = fit_standardizer(volumes)
		with open(standardizers_path+'standardizer_volumes.pkl', 'wb') as f:
			pickle.dump(standardizer, f)
	volumes_standardized = standardize(volumes, standardizer)

	# Volume increased in last X observations
	inc_vol_last1 = [utils_features.volume_increased_past(data_dic, time, 1) for time in times]
	inc_vol_last2 = [utils_features.volume_increased_past(data_dic, time, 2) for time in times]
	inc_vol_last3 = [utils_features.volume_increased_past(data_dic, time, 3) for time in times]
	inc_vol_last4 = [utils_features.volume_increased_past(data_dic, time, 4) for time in times]
	inc_vol_last5 = [utils_features.volume_increased_past(data_dic, time, 5) for time in times]
	inc_vol_last6 = [utils_features.volume_increased_past(data_dic, time, 6) for time in times]

	# Trade increased in this observation
	inc_trades = [utils_features.attribute_increased_for_time(data_dic, time, 'trades_count') for time in times]

	# Standardized N of trades
	trades = [data_dic[time]['trades_count'] for time in times]
	if for_prediction:
		with open(standardizers_path+'standardizer_trades.pkl', 'rb') as f:
			standardizer = pickle.load(f)
	else:
		standardizer = fit_standardizer(trades)
		with open(standardizers_path+'standardizer_trades.pkl', 'wb') as f:
			pickle.dump(standardizer, f)
	trades_standardized = standardize(trades, standardizer)

	# Trade increased in last X observations
	inc_trade_last1 = [utils_features.trades_increased_past(data_dic, time, 1) for time in times]
	inc_trade_last2 = [utils_features.trades_increased_past(data_dic, time, 1) for time in times]
	inc_trade_last3 = [utils_features.trades_increased_past(data_dic, time, 1) for time in times]
	inc_trade_last4 = [utils_features.trades_increased_past(data_dic, time, 1) for time in times]
	inc_trade_last5 = [utils_features.trades_increased_past(data_dic, time, 1) for time in times]
	inc_trade_last6 = [utils_features.trades_increased_past(data_dic, time, 1) for time in times]

	# Standardized price ranges (open-close)
	price_ranges_oc = [utils_features.price_range_oc(data_dic, time) for time in times]
	standardizer_path = standardizers_path + 'standardizer_price_ranges_oc.pkl'
	if for_prediction:
		with open(standardizer_path, 'rb') as f:
			standardizer = pickle.load(f)
	else:
		standardizer = fit_standardizer(price_ranges_oc)
		with open(standardizer_path, 'wb') as f:
			pickle.dump(standardizer, f)
	price_ranges_oc_standardized = standardize(price_ranges_oc, standardizer)

	# Standardized price ranges (high-low)
	price_ranges_hl = [utils_features.price_range_hl(data_dic, time) for time in times]
	standardizer_path = standardizers_path + 'standardizer_price_ranges_hl.pkl'
	if for_prediction:
		with open(standardizer_path, 'rb') as f:
			standardizer = pickle.load(f)
	else:
		standardizer = fit_standardizer(price_ranges_hl)
		with open(standardizer_path, 'wb') as f:
			pickle.dump(standardizer, f)
	price_ranges_hl_standardized = standardize(price_ranges_hl, standardizer)

	# Price range bins (OC)
	price_ranges_oc_np = np.array(price_ranges_oc).reshape(-1, 1)
	binner_path = binners_path + 'standardizer_price_range_bins_oc.pkl'
	if for_prediction:
		with open(binner_path, 'rb') as f:
			binner = pickle.load(f)
	else:
		binner = preprocessing.KBinsDiscretizer(n_bins=5, encode='onehot-dense', strategy='uniform')
		binner.fit(price_ranges_oc_np)
		with open(binner_path, 'wb') as f:
			pickle.dump(binner, f)
	bins = binner.transform(price_ranges_oc_np)
	price_ranges_oc_bin1 = bins[:, 0]
	price_ranges_oc_bin2 = bins[:, 1]
	price_ranges_oc_bin3 = bins[:, 2]
	price_ranges_oc_bin4 = bins[:, 3]
	price_ranges_oc_bin5 = bins[:, 4]

	# Price range bins (OC) quantiles
	binner_path = binners_path + 'standardizer_price_range_bins_oc_quantiles.pkl'
	if for_prediction:
		with open(binner_path, 'rb') as f:
			binner = pickle.load(f)
	else:
		binner = preprocessing.KBinsDiscretizer(n_bins=10, encode='onehot-dense', strategy='quantile')
		binner.fit(price_ranges_oc_np)
		with open(binner_path, 'wb') as f:
			pickle.dump(binner, f)
	bins = binner.transform(price_ranges_oc_np)
	price_ranges_oc_bin1_quant = bins[:, 0]
	price_ranges_oc_bin2_quant = bins[:, 1]
	price_ranges_oc_bin3_quant = bins[:, 2]
	price_ranges_oc_bin4_quant = bins[:, 3]
	price_ranges_oc_bin5_quant = bins[:, 4]
	price_ranges_oc_bin6_quant = bins[:, 5]
	price_ranges_oc_bin7_quant = bins[:, 6]
	price_ranges_oc_bin8_quant = bins[:, 7]
	price_ranges_oc_bin9_quant = bins[:, 8]
	price_ranges_oc_bin10_quant = bins[:, 9]

	# Price range bins (HL)
	price_ranges_hl_np = np.array(price_ranges_hl).reshape(-1, 1)
	binner_path = binners_path + 'standardizer_price_range_bins_hl.pkl'
	if for_prediction:
		with open(binner_path, 'rb') as f:
			binner = pickle.load(f)
	else:
		binner = preprocessing.KBinsDiscretizer(n_bins=5, encode='onehot-dense', strategy='uniform')
		binner.fit(price_ranges_hl_np)
		with open(binner_path, 'wb') as f:
			pickle.dump(binner, f)
	bins = binner.transform(price_ranges_hl_np)
	price_ranges_hl_bin1 = bins[:, 0]
	price_ranges_hl_bin2 = bins[:, 1]
	price_ranges_hl_bin3 = bins[:, 2]
	price_ranges_hl_bin4 = bins[:, 3]
	price_ranges_hl_bin5 = bins[:, 4]

	# Price range bins (HL) quantiles
	binner_path = binners_path + 'standardizer_price_range_bins_hl_quantiles.pkl'
	if for_prediction:
		with open(binner_path, 'rb') as f:
			binner = pickle.load(f)
	else:
		binner = preprocessing.KBinsDiscretizer(n_bins=10, encode='onehot-dense', strategy='quantile')
		binner.fit(price_ranges_hl_np)
		with open(binner_path, 'wb') as f:
			pickle.dump(binner, f)
	bins = binner.transform(price_ranges_hl_np)
	price_ranges_hl_bin1_quant = bins[:, 0]
	price_ranges_hl_bin2_quant = bins[:, 1]
	price_ranges_hl_bin3_quant = bins[:, 2]
	price_ranges_hl_bin4_quant = bins[:, 3]
	price_ranges_hl_bin5_quant = bins[:, 4]
	price_ranges_hl_bin6_quant = bins[:, 5]
	price_ranges_hl_bin7_quant = bins[:, 6]
	price_ranges_hl_bin8_quant = bins[:, 7]
	price_ranges_hl_bin9_quant = bins[:, 8]
	price_ranges_hl_bin10_quant = bins[:, 9]

	# Max price is open price
	max_price_is_open = [utils_features.max_price_is_open_fn(data_dic, time) for time in times]

	# Max price is close price
	max_price_is_close = [utils_features.max_price_is_close_fn(data_dic, time) for time in times]

	# Min price is open price
	min_price_is_open = [utils_features.min_price_is_open_fn(data_dic, time) for time in times]

	# Min price is close price
	min_price_is_close = [utils_features.min_price_is_close_fn(data_dic, time) for time in times]

	# OC price range increased
	inc_price_range_oc = [utils_features.price_range_oc_increase(data_dic, time) for time in times]

	# HL price range increased
	inc_price_range_hl = [utils_features.price_range_hl_increase(data_dic, time) for time in times]

	# Max price is within 1%, 0.1%, 0.05%, 0.01% of close price
	max_close_01 = [utils_features.x_is_within_gap(data_dic[time]['price_high'], data_dic[time]['price_close'], 0.01) for time in times]
	max_close_001 = [utils_features.x_is_within_gap(data_dic[time]['price_high'], data_dic[time]['price_close'], 0.001) for time in times]
	max_close_0005 = [utils_features.x_is_within_gap(data_dic[time]['price_high'], data_dic[time]['price_close'], 0.0005) for time in times]
	max_close_0001 = [utils_features.x_is_within_gap(data_dic[time]['price_high'], data_dic[time]['price_close'], 0.0001) for time in times]

	# Max price is within 1%, 0.1%, 0.05%, 0.01% of open price
	max_open_01 = [utils_features.x_is_within_gap(data_dic[time]['price_high'], data_dic[time]['price_open'], 0.01) for time in times]
	max_open_001 = [utils_features.x_is_within_gap(data_dic[time]['price_high'], data_dic[time]['price_open'], 0.001) for time in times]
	max_open_0005 = [utils_features.x_is_within_gap(data_dic[time]['price_high'], data_dic[time]['price_open'], 0.0005) for time in times]
	max_open_0001 = [utils_features.x_is_within_gap(data_dic[time]['price_high'], data_dic[time]['price_open'], 0.0001) for time in times]

	# Min price is within 1%, 0.1%, 0.05%, 0.01% of close price
	min_close_01 = [utils_features.x_is_within_gap(data_dic[time]['price_low'], data_dic[time]['price_close'], 0.01) for time in times]
	min_close_001 = [utils_features.x_is_within_gap(data_dic[time]['price_low'], data_dic[time]['price_close'], 0.001) for time in times]
	min_close_0005 = [utils_features.x_is_within_gap(data_dic[time]['price_low'], data_dic[time]['price_close'], 0.0005) for time in times]
	min_close_0001 = [utils_features.x_is_within_gap(data_dic[time]['price_low'], data_dic[time]['price_close'], 0.0001) for time in times]

	# Min price is within 1%, 0.1%, 0.05%, 0.01% of open price
	min_open_01 = [utils_features.x_is_within_gap(data_dic[time]['price_low'], data_dic[time]['price_open'], 0.01) for time in times]
	min_open_001 = [utils_features.x_is_within_gap(data_dic[time]['price_low'], data_dic[time]['price_open'], 0.001) for time in times]
	min_open_0005 = [utils_features.x_is_within_gap(data_dic[time]['price_low'], data_dic[time]['price_open'], 0.0005) for time in times]
	min_open_0001 = [utils_features.x_is_within_gap(data_dic[time]['price_low'], data_dic[time]['price_open'], 0.0001) for time in times]


	# Putting all together
	data = [
		close_prices_standardized,
		inc_price_last1,
		inc_price_last2,
		inc_price_last3,
		inc_price_last4,
		inc_price_last5,
		inc_price_last6,
		volumes_standardized,
		inc_vol_last1,
		inc_vol_last2,
		inc_vol_last3,
		inc_vol_last4,
		inc_vol_last5,
		inc_vol_last6,
		trades_standardized,
		inc_trade_last1,
		inc_trade_last2,
		inc_trade_last3,
		inc_trade_last4,
		inc_trade_last5,
		inc_trade_last6,
		price_ranges_oc_standardized,
		#inc_price_range_oc_last1,
		#inc_price_range_oc_last2,
		#inc_price_range_oc_last3,
		#inc_price_range_oc_last4,
		#inc_price_range_oc_last5,
		#inc_price_range_oc_last6,
		price_ranges_hl_standardized,
		#inc_price_range_hl_last1,
		#inc_price_range_hl_last2,
		#inc_price_range_hl_last3,
		#inc_price_range_hl_last4,
		#inc_price_range_hl_last5,
		#inc_price_range_hl_last6,
		price_ranges_oc_bin1,
		price_ranges_oc_bin2,
		price_ranges_oc_bin3,
		price_ranges_oc_bin4,
		price_ranges_oc_bin5,
		price_ranges_oc_bin1_quant,
		price_ranges_oc_bin2_quant,
		price_ranges_oc_bin3_quant,
		price_ranges_oc_bin4_quant,
		price_ranges_oc_bin5_quant,
		price_ranges_oc_bin6_quant,
		price_ranges_oc_bin7_quant,
		price_ranges_oc_bin8_quant,
		price_ranges_oc_bin9_quant,
		price_ranges_oc_bin10_quant,
		price_ranges_hl_bin1,
		price_ranges_hl_bin2,
		price_ranges_hl_bin3,
		price_ranges_hl_bin4,
		price_ranges_hl_bin5,
		price_ranges_hl_bin1_quant,
		price_ranges_hl_bin2_quant,
		price_ranges_hl_bin3_quant,
		price_ranges_hl_bin4_quant,
		price_ranges_hl_bin5_quant,
		price_ranges_hl_bin6_quant,
		price_ranges_hl_bin7_quant,
		price_ranges_hl_bin8_quant,
		price_ranges_hl_bin9_quant,
		price_ranges_hl_bin10_quant,
		max_price_is_open,
		max_price_is_close,
		max_close_01,
		max_close_001,
		max_close_0005,
		max_close_0001,
		max_open_01,
		max_open_001,
		max_open_0005,
		max_open_0001,
		min_price_is_open,
		min_price_is_close,
		min_close_01,
		min_close_001,
		min_close_0005,
		min_close_0001,
		min_open_01,
		min_open_001,
		min_open_0005,
		min_open_0001,
		inc_price,
		inc_vol,
		inc_trades,
		inc_price_range_oc,
		inc_price_range_hl,
	]

	return data

def prediction_from_net(X, model, threshold=None):

	'''
	Estimate price increase prediction
	'''

	X = torch.tensor(X).float()

	with torch.no_grad():
		pred_logit = model(X).squeeze()
		score = torch.sigmoid(pred_logit)
		print('Score predicted: {}'.format(round(score.item(), 2)))
		if threshold:
			pred = torch.where(score > threshold, 1, 0)
		else:
			pred = torch.round(score)

	return pred.item()
