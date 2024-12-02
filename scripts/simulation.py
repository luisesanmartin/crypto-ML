import pickle
import sys
sys.path.insert(1, './utils')
import utils_simulation
import utils_data

def main():

	data_file = '../data/raw/data_BITSTAMP_SPOT_BTC_USD_10MIN_2024-09-07T20:10:00_2024-11-19T23:00:00.pkl'
	with open(data_file, 'rb') as f:
		data = pickle.load(f)
	data_dic = utils_data.make_data_dic(data)
	results_file = '../data/results/simulations-manual-rules.csv'

	utils_simulation.simulate_all(
		data_dic,
		results_file,
		amount_to_trade = 100
	)

if __name__ == '__main__':
	main()