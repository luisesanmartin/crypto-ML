SYMBOL_ID = 'BITSTAMP_SPOT_BTC_USD'
URL = 'https://rest.coinapi.io/v1/ohlcv/{}/history'
PERIOD_DATA = '10MIN'
PERIOD_DATA_MIN = 10
TIME_FMT = '%Y-%m-%dT%H:%M:%S'
DATA_MAX = 100000
MARGIN = 0.008 # 0.4% is the fee for buying and selling in BS
FEE_RATE = 0.004
VALLEY_PERIODS = 18 # this times 10 minutes divided by 60 is the number of hours
POS_WEIGHTS = 74168/5184 # neg samples / pos samples
TEST_SIZE = 0.2
PREDICT_THRESHOLD = 0.7

# Columns in working df
COLS = [
	'time',				# Obs ID
	'valley',		    # Y
	'price_close_sd',	# X variables from this one on
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
	'price_ranges_oc_standardized',
	'price_ranges_hl_standardized',
	'price_ranges_oc_bin1',
	'price_ranges_oc_bin2',
	'price_ranges_oc_bin3',
	'price_ranges_oc_bin4',
	'price_ranges_oc_bin5',
	'max_price_is_open',
	'max_price_is_close',
	'min_price_is_open',
	'min_price_is_close',
	'inc_price',
	'inc_vol',
	'inc_trades'
]