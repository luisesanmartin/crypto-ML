import pandas as pd
import pickle
import sys
sys.path.insert(1, './utils')
import utils_time
import utils_data_wrangling as utils

###############
## Load data ##
###############

print("1: Reading data...")

file = '../data/raw/data_10MIN_2024-06-21T00:10:00_2022-07-27T13:50:00.pkl'
#file = '../data/raw/data_min.pkl'
with open(file, 'rb') as f:
	data = pickle.load(f)

data_dic = utils.make_data_dic(data)

######################
## Sample selection ##
######################

###############
## Variables ##
###############

print("2: Creating variables...")

# ID variable: end time of period
times = list(data_dic.keys())

# Predicted variable: price increased in the future
increased_future = [utils.price_increased_next(data_dic, time, 1) for time in times]

# Price increased in this observation
inc_price = [utils.price_increased_next(data_dic, time, 0) for time in times]

# Standardized close price
close_prices = [data_dic[time]['price_close'] for time in times]
standardizer = utils.fit_standardizer(close_prices)
with open('../data/models/standardizer_prices.pkl', 'wb') as f:
	pickle.dump(standardizer, f)
close_prices_standardized = utils.standardize(close_prices, standardizer)

# Price increase in last X observations
inc_price_last1 = [utils.price_increased_next(data_dic, time, -1) for time in times]
inc_price_last2 = [utils.price_increased_next(data_dic, time, -2) for time in times]
inc_price_last3 = [utils.price_increased_next(data_dic, time, -3) for time in times]
inc_price_last4 = [utils.price_increased_next(data_dic, time, -4) for time in times]
inc_price_last5 = [utils.price_increased_next(data_dic, time, -5) for time in times]
inc_price_last6 = [utils.price_increased_next(data_dic, time, -6) for time in times]

# Volume increased in this observation
inc_vol = [utils.attribute_increased_for_time(data_dic, time, 'volume_traded') for time in times]

# Standardized volume traded
volumes = [data_dic[time]['volume_traded'] for time in times]
standardizer = utils.fit_standardizer(volumes)
with open('../data/models/standardizer_volumes.pkl', 'wb') as f:
	pickle.dump(standardizer, f)
volumes_standardized = utils.standardize(volumes, standardizer)

# Volume increased in last X observations
inc_vol_last1 = [utils.volume_increased_past(data_dic, time, 1) for time in times]
inc_vol_last2 = [utils.volume_increased_past(data_dic, time, 2) for time in times]
inc_vol_last3 = [utils.volume_increased_past(data_dic, time, 3) for time in times]
inc_vol_last4 = [utils.volume_increased_past(data_dic, time, 4) for time in times]
inc_vol_last5 = [utils.volume_increased_past(data_dic, time, 5) for time in times]
inc_vol_last6 = [utils.volume_increased_past(data_dic, time, 6) for time in times]

# Trade increased in this observation
inc_trades = [utils.attribute_increased_for_time(data_dic, time, 'trades_count') for time in times]

# Standardized N of trades
trades = [data_dic[time]['trades_count'] for time in times]
standardizer = utils.fit_standardizer(trades)
with open('../data/models/standardizer_trades.pkl', 'wb') as f:
	pickle.dump(standardizer, f)
trades_standardized = utils.standardize(trades, standardizer)

# Trade increased in last X observations
inc_trade_last1 = [utils.trades_increased_past(data_dic, time, 1) for time in times]
inc_trade_last2 = [utils.trades_increased_past(data_dic, time, 1) for time in times]
inc_trade_last3 = [utils.trades_increased_past(data_dic, time, 1) for time in times]
inc_trade_last4 = [utils.trades_increased_past(data_dic, time, 1) for time in times]
inc_trade_last5 = [utils.trades_increased_past(data_dic, time, 1) for time in times]
inc_trade_last6 = [utils.trades_increased_past(data_dic, time, 1) for time in times]

# Max price is open price
max_price_is_open = [utils.max_price_is_open(data_dic, time) for time in times]

# Max price is close price
max_price_is_close = [utils.max_price_is_close(data_dic, time) for time in times]

# Min price is open price
min_price_is_open = [utils.min_price_is_open(data_dic, time) for time in times]

# Min price is close price
min_price_is_close = [utils.min_price_is_close(data_dic, time) for time in times]

######################
## Train/test split ##
######################


#####################
## Final dataframe ##
#####################

print('3: Saving dataframe...')

# Putting everything together in one dataframe
cols = [
	'time',
	'increased',
	'price_close_sd',
	'inc_price_last1',
	'inc_price_last2',
	'inc_price_last3',
	'inc_price_last4',
	'inc_price_last5',
	'inc_price_last6',
	'vol_sd',
	'inc_vol_last1',
	'inc_vol_last2',
	'inc_vol_last3',
	'inc_vol_last4',
	'inc_vol_last5',
	'inc_vol_last6',
	'trades_sd',
	'inc_trades_last_1',
	'inc_trades_last_2',
	'inc_trades_last_3',
	'inc_trades_last_4',
	'inc_trades_last_5',
	'inc_trades_last_6',
	'max_price_is_open',
	'max_price_is_close',
	'min_price_is_open',
	'min_price_is_close',
	'inc_price',
	'inc_vol',
	'inc_trades'
	]
data = [
	times,
	increased_future,
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
	max_price_is_open,
	max_price_is_close,
	min_price_is_open,
	min_price_is_close,
	inc_price,
	inc_vol,
	inc_trades
	]
df = pd.DataFrame(dict(zip(cols, data)))
n1 = len(df)

# Removing obs with nan
df = df.dropna(how='any')
n2 = len(df)
print('\tObservations: {}'.format(n2))
print('\tKept {}% of initial obs after dropping columns with missings'.format(round(n2/n1*100)))

# Exporting
file = '../data/working/data.csv'
df.to_csv(file, index=False)
