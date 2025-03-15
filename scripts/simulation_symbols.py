import os
import sys
import multiprocessing
sys.path.insert(1, './utils')
import utils_data
import utils_simulation
import objects

raw_data_folder = '../data/raw/bitstamp'
symbols = objects.BITSTAMP_SYMBOLS
start_date = objects.DATA_START
end_date = objects.DATA_END
step = objects.GAP_EPOCH
files = [f'{raw_data_folder}/data_{symbol}_{start_date}_{end_date}_step{step}.pkl' for symbol in symbols]
all_data = {f.split('_')[1]: utils_data.open_pickle(f) for f in files}
data_dic = utils_data.make_data_dic_bitstamp(all_data)

def simulate(period):

	results_file = f'../data/results/simulations-manual-rules-symbols-period{period}.csv'
	results_path = f'../data/results/period{period}'
	if not os.path.exists(results_path):
		os.makedirs(results_path)
	utils_simulation.simulate_all_symbols(
		data_dic = data_dic,
		results_file = results_file,
		detailed_results_path = results_path,
		amount_to_trade = 1000,
		periods = [period]
	)

	return True

def main():

	process_pool = multiprocessing.Pool(processes=16)
	process_pool.map(simulate, objects.PERIODS)

if __name__ == '__main__':
	main()