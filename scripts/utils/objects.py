SYMBOL_ID = 'BITSTAMP_SPOT_BTC_USD'
SYMBOL_ID_BITSTAMP = 'btcusd'
URL = 'https://rest.coinapi.io/v1/ohlcv/{}/history'
URL_BITSTAMP = 'https://www.bitstamp.net/api/v2/ohlc/{}/'
PERIOD_DATA = '10MIN'
PERIOD_DATA_MIN = 10
TIME_FMT = '%Y-%m-%dT%H:%M:%S'
DATA_MAX = 100000
MARGIN = 0.01
FEE_RATE = 0.004
VALLEY_PERIODS = 18 # this times 10 minutes divided by 60 is the number of hours
POS_WEIGHTS = (79351-6040)/6040 # neg samples / pos samples
TEST_SIZE = 0.2
PREDICT_THRESHOLD = 0.7
#PERIODS = [5//5, 30//5, 60//5, 90//5, 120//5, 180//5, 240//5, 300//5, 360//5, 480//5, 600//5, 720//5, 1080//5, 1440//5, 2160//5]
PERIODS = [1, 5, 10, 20, 30, 45, 60, 180, 360, 720, 1440, 2160, 2880]
BUY_RATES = [-.1, -.07, -.05, -.03, -.015, .015, .03, .05, .07, .1]
SELL_RATES = [.01, .02, .03, .04, .05, .06, .07, .08, .09, .1]
CUT_LOSS_RATES = [.01, .02, .03, .04, .05, .06, .07, .08, .09, .1]
BUY_RATE = -.05
SELL_RATE = .05
CUT_LOSS_RATE = -.1
PERIOD = 1
GAP_EPOCH = 60 # one minute
DATA_START = '2024-12-15'
DATA_END = '2025-03-14'

BITSTAMP_SYMBOLS = [
	'btcusd',
	'ethusd',
	'xrpusd',
	'solusd',
	'ltcusd',
	'aaveusd',
	'xlmusd',
	'suiusd',
	'dogeusd',
	'hbarusd',
	'adausd',
	'linkusd',
	'avaxusd',
	'xdcusd',
	'shibusd',
	'dotusd',
	'maticusd',
	'uniusd',
	'ftmusd',
	'pepeusd'
	]

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
	'price_ranges_oc_bin1_quant',
	'price_ranges_oc_bin2_quant',
	'price_ranges_oc_bin3_quant',
	'price_ranges_oc_bin4_quant',
	'price_ranges_oc_bin5_quant',
	'price_ranges_oc_bin6_quant',
	'price_ranges_oc_bin7_quant',
	'price_ranges_oc_bin8_quant',
	'price_ranges_oc_bin9_quant',
	'price_ranges_oc_bin10_quant',
	'price_ranges_hl_bin1',
	'price_ranges_hl_bin2',
	'price_ranges_hl_bin3',
	'price_ranges_hl_bin4',
	'price_ranges_hl_bin5',
	'price_ranges_hl_bin1_quant',
	'price_ranges_hl_bin2_quant',
	'price_ranges_hl_bin3_quant',
	'price_ranges_hl_bin4_quant',
	'price_ranges_hl_bin5_quant',
	'price_ranges_hl_bin6_quant',
	'price_ranges_hl_bin7_quant',
	'price_ranges_hl_bin8_quant',
	'price_ranges_hl_bin9_quant',
	'price_ranges_hl_bin10_quant',
	'max_price_is_open',
	'max_price_is_close',
	'max_close_01',
	'max_close_001',
	'max_close_0005',
	'max_close_0001',
	'max_open_01',
	'max_open_001',
	'max_open_0005',
	'max_open_0001',
	'min_price_is_open',
	'min_price_is_close',
	'min_close_01',
	'min_close_001',
	'min_close_0005',
	'min_close_0001',
	'min_open_01',
	'min_open_001',
	'min_open_0005',
	'min_open_0001',
	'inc_price',
	'inc_vol',
	'inc_trades',
	'inc_price_range_oc',
	'inc_price_range_hl',
	'price_close_diffs_std',
	'price_open_diffs_std',
	'price_max_diffs_std',
	'price_min_diffs_std',
	'volume_diffs_std',
	'trades_diffs_std',
	'avg_volumes_per_trade_std'
]