import pickle
import sys
sys.path.insert(1, './utils')
import utils_fetch
import objects

time_start = '2024-09-07T20:00:00.000'
time_end = '2024-11-19T23:00:00.000'
limit = 11000
data = utils_fetch.get_data_with_limits(time_start, time_end, limit)


end = data[-1]['time_period_end'].split('.')[0]
start = data[0]['time_period_end'].split('.')[0]
frequency = objects.PERIOD_DATA

file = '../data/raw/data_{}_{}_{}_{}.pkl'.format(objects.SYMBOL_ID, frequency, start, end)

with open(file, 'wb') as f:
	pickle.dump(data, f)
