import os
import sys
sys.path.insert(1, './utils')
import utils_data
import utils_simulation

raw_data_folder = '../data/raw/bitstamp/'
results_file = '../data/results/simulations-manual-rules-symbols.csv'

def main():

	files = [f'{raw_data_folder}{f}' for f in os.listdir(raw_data_folder)]
	all_data = {f.split('_')[1]: utils_data.open_pickle(f) for f in files}
	data_dic = utils_data.make_data_dic_bitstamp(all_data)

	utils_simulation.simulate_all_symbols(
		data_dic,
		results_file,
		amount_to_trade = 1000
	)

	return True

if __name__ == '__main__':
	main()