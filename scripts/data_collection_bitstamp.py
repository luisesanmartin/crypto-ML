import os
import pickle
import time
import sys
sys.path.insert(1, './utils')
import objects
import utils_fetch

symbols = objects.BITSTAMP_SYMBOLS
raw_data_folder = '../data/raw/bitstamp'
start = objects.DATA_START
end = objects.DATA_END
step = objects.GAP_EPOCH

def main():

	for symbol in symbols:

		print(f'Getting data for {symbol}')
		file = f'{raw_data_folder}/data_{symbol}_{start}_{end}_step{step}.pkl'
		if os.path.isfile(file):
			continue

		data = utils_fetch.get_data_bitstamp_from_to(start, end, symbol, step)
		with open(file, 'wb') as f:
			pickle.dump(data, f)

		time.sleep(1)

	return True

if __name__ == '__main__':
	main()