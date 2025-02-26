import os
import sys
import multiprocessing
sys.path.insert(1, './utils')
import utils_data
import utils_simulation
import objects

raw_data_folder = '../data/raw/bitstamp/'
files = [f'{raw_data_folder}{f}' for f in os.listdir(raw_data_folder)]
all_data = {f.split('_')[1]: utils_data.open_pickle(f) for f in files}
data_dic = utils_data.make_data_dic_bitstamp(all_data)

def simulate(period):

	results_file = f'../data/results/simulations-manual-rules-symbols-period{period}.csv'
	utils_simulation.simulate_all_symbols(
		data_dic = data_dic,
		results_file = results_file,
		amount_to_trade = 1000,
		periods = [period]
	)

	return True

def main():

	process_pool = multiprocessing.Pool(processes=16)
	process_pool.map(simulate, objects.PERIODS)

if __name__ == '__main__':
	main()