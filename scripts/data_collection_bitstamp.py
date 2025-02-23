import os
import pickle
import time
import sys
sys.path.insert(1, './utils')
import objects
import utils_fetch

symbols = objects.BITSTAMP_SYMBOLS
raw_data_folder = '../data/raw/bitstamp'
start = '2024-11-15'
end = '2025-02-15'

def main():

	for symbol in symbols:

		print(f'Getting data for {symbol}')
		file = f'{raw_data_folder}/data_{symbol}_{start}_{end}.pkl'
		if os.path.isfile(file):
			continue

		data = utils_fetch.get_data_bitstamp_from_to(start, end, symbol)
		with open(file, 'wb') as f:
			pickle.dump(data, f)

		time.sleep(1)

	return True

if __name__ == '__main__':
	main()