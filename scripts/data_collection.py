import pickle
import sys
sys.path.insert(1, './utils')
import utils_fetch
import objects

data = utils_fetch.get_data_max()
data = data[1:] #drop first obs as it's going to be incomplete

end = data[0]['time_period_end'].split('.')[0]
start = data[-1]['time_period_end'].split('.')[0]
frequency = objects.PERIOD_DATA

file = '../data/raw/data_{}_{}_{}_{}.pkl'.format(objects.SYMBOL_ID, frequency, start, end)

with open(file, 'wb') as f:
	pickle.dump(data, f)
