import os
import sys
import multiprocessing
from datetime import datetime, timedelta
sys.path.insert(1, './utils')
import utils_data
import utils_simulation
import objects
import pandas as pd

raw_data_folder = '../data/raw/bitstamp'
symbols = objects.BITSTAMP_SYMBOLS
start_date = objects.DATA_START
end_date = objects.DATA_END
step = objects.GAP_EPOCH

# Load all data
files = [f'{raw_data_folder}/data_{symbol}_{start_date}_{end_date}_step{step}.pkl' for symbol in symbols]
all_data = {f.split('_')[1]: utils_data.open_pickle(f) for f in files}
data_dic = utils_data.make_data_dic_bitstamp(all_data)

# Get all timestamps and sort them
all_times = sorted(list(data_dic.keys()))

# Calculate key dates
data_start_ts = all_times[0]
data_end_ts = all_times[-1]
opt_window_seconds = objects.WALK_FORWARD_OPT_WINDOW_DAYS * 24 * 3600
test_window_seconds = objects.WALK_FORWARD_TEST_WINDOW_DAYS * 24 * 3600

# Optimization period ends X days before data end
opt_period_end_ts = data_end_ts - objects.WALK_FORWARD_OPT_WINDOW_DAYS * 24 * 3600

# Create results directories
results_dir = '../data/results/walk_forward'
if not os.path.exists(results_dir):
    os.makedirs(results_dir)

print("=" * 80)
print("WALK-FORWARD OPTIMIZATION AND TESTING")
print("=" * 80)
print(f"Data range: {datetime.fromtimestamp(data_start_ts)} to {datetime.fromtimestamp(data_end_ts)}")
print(f"Optimization window: {objects.WALK_FORWARD_OPT_WINDOW_DAYS} days")
print(f"Test window: {objects.WALK_FORWARD_TEST_WINDOW_DAYS} days")
print(f"Optimization period ends: {datetime.fromtimestamp(opt_period_end_ts)}")
print(f"Total timestamps loaded: {len(all_times)}")
print("=" * 80)

def run_window_optimization_period(args):
	'''
	Run optimization for a specific period within a window.
	This function is called in parallel for each period.
	'''
	period, window_number, window_opt_start, window_opt_end, data_dic, results_dir = args
	
	results_file = f'{results_dir}/window_{window_number}_optimization_period{period}.csv'
	detail_path = f'{results_dir}/window_{window_number}_period{period}_detail'
	
	if not os.path.exists(detail_path):
		os.makedirs(detail_path)
	
	utils_simulation.simulate_all_symbols_date_range(
		data_dic=data_dic,
		results_file=results_file,
		detailed_results_path=detail_path,
		amount_to_trade=1000,
		start_timestamp=window_opt_start,
		end_timestamp=window_opt_end,
		periods=[period],
		buy_rates=objects.BUY_RATES,
		sell_rates=objects.SELL_RATES,
		cut_loss_rates=objects.CUT_LOSS_RATES
	)
	return True

# Collect all test results
all_test_results = []
window_number = 1

# Step through the data in X-day windows
current_window_end = data_start_ts + opt_window_seconds

while current_window_end <= opt_period_end_ts:
	
	window_opt_start = current_window_end - opt_window_seconds
	window_opt_end = current_window_end
	window_test_start = current_window_end + 1  # +1 to avoid overlap
	window_test_end = window_test_start + test_window_seconds - 1
	
	# Make sure test window doesn't exceed data
	if window_test_end > data_end_ts:
		window_test_end = data_end_ts
	
	print(f"\n{'='*80}")
	print(f"WINDOW {window_number}")
	print(f"{'='*80}")
	print(f"Optimization: {datetime.fromtimestamp(window_opt_start)} to {datetime.fromtimestamp(window_opt_end)}")
	print(f"Testing:      {datetime.fromtimestamp(window_test_start)} to {datetime.fromtimestamp(window_test_end)}")
	
	# Step 1: Run optimization (parallelized by period)
	print(f"\n[STEP 1] Running optimization for window {window_number} (parallelized by period)...")
	
	# Prepare arguments for parallel execution
	period_args = [
		(period, window_number, window_opt_start, window_opt_end, data_dic, results_dir)
		for period in objects.PERIODS
	]
	
	process_pool = multiprocessing.Pool(processes=objects.NUM_PROCESSES)
	process_pool.map(run_window_optimization_period, period_args)
	process_pool.close()
	process_pool.join()
	
	# Combine results from all periods
	print("Combining results from all periods...")
	all_results = []
	for period in objects.PERIODS:
		results_file = f'{results_dir}/window_{window_number}_optimization_period{period}.csv'
		if os.path.exists(results_file):
			df = pd.read_csv(results_file)
			all_results.append(df)
	
	combined_df = pd.concat(all_results, ignore_index=True)
	opt_results_file = f'{results_dir}/window_{window_number}_optimization_results.csv'
	combined_df.to_csv(opt_results_file, index=None)
	
	# Extract best parameters
	print(f"\n[STEP 2] Extracting best parameters for window {window_number}...")
	best_params = utils_simulation.get_best_parameters(opt_results_file)
	
	print(f"Best parameters found:")
	print(f"  - Period: {best_params['period']}")
	print(f"  - Buy rate: {best_params['buy_rate']}")
	print(f"  - Sell rate: {best_params['sell_rate']}")
	print(f"  - Cut loss rate: {best_params['cut_loss_rate']}")
	print(f"  - Return rate: {best_params['return_rate']:.2f}%")
	
	# Step 3: Test with best parameters
	print(f"\n[STEP 3] Testing with best parameters on next {objects.WALK_FORWARD_TEST_WINDOW_DAYS} days...")
	
	# Filter data for test period
	test_data_dic = utils_simulation.filter_data_dic_by_time_range(
		data_dic,
		window_test_start,
		window_test_end
	)
	
	times = sorted(list(test_data_dic.keys()))
	
	if len(times) < best_params['period']:
		print(f"Not enough data in test window for period {best_params['period']}. Skipping.")
		current_window_end += opt_window_seconds
		window_number += 1
		continue
	
	# Run simulation with best parameters
	results_detailed = []
	hold = False
	amount = 1000
	crypto = 0
	total_fees = 0
	n_trades_profit = 0
	n_trades_loss = 0
	n_trades = 0
	last_purchase_price = None
	symbol_holding = None
	
	cols2 = [
		'Time',
		'Amount',
		'Total fees',
		'N trades-profit',
		'N trades-loss',
		'N trades',
		'Symbol holding']
	
	for time in times[best_params['period']:]:
		results_detailed.append([time, amount, total_fees, n_trades_profit, n_trades_loss, n_trades, symbol_holding])
		
		hold, crypto, amount, total_fees, last_purchase_price, symbol_holding, n_trades_profit, n_trades_loss, n_trades = \
			utils_simulation.simulate_one_symbols(
				test_data_dic,
				time,
				hold,
				amount,
				crypto,
				total_fees,
				n_trades_profit,
				n_trades_loss,
				n_trades,
				last_purchase_price,
				best_params['period'],
				best_params['buy_rate'],
				best_params['sell_rate'],
				best_params['cut_loss_rate'],
				symbol_holding)
	
	# Save detailed results
	df = pd.DataFrame(columns=cols2, data=results_detailed)
	detailed_file = f'{results_dir}/window_{window_number}_test_detailed.csv'
	df.to_csv(detailed_file, index=None)
	
	# Calculate final results
	if hold:  # sell at end
		current_price = float(test_data_dic[time][symbol_holding]['close'])
		amount = crypto * current_price
		fee = amount * objects.FEE_RATE
		total_fees += fee
	
	amount_used = round(1000 + total_fees, 2)
	profits = round(amount - amount_used, 2)
	return_rate = (profits / amount_used) * 100 if amount_used != 0 else 0
	
	print("\n" + "-" * 80)
	print("TEST RESULTS FOR THIS WINDOW")
	print("-" * 80)
	print(f"Amount used: ${amount_used}")
	print(f"Final amount: ${round(amount, 2)}")
	print(f"Trades (profit): {n_trades_profit}")
	print(f"Trades (loss): {n_trades_loss}")
	print(f"Total trades: {n_trades}")
	print(f"Total fees: ${total_fees}")
	print(f"Profits: ${profits}")
	print(f"Return rate: {return_rate:.2f}%")
	
	# Save window results
	test_result = {
		'Window': window_number,
		'Opt start': datetime.fromtimestamp(window_opt_start),
		'Opt end': datetime.fromtimestamp(window_opt_end),
		'Test start': datetime.fromtimestamp(window_test_start),
		'Test end': datetime.fromtimestamp(window_test_end),
		'Period': best_params['period'],
		'Buy rate': best_params['buy_rate'],
		'Sell rate': best_params['sell_rate'],
		'Cut loss rate': best_params['cut_loss_rate'],
		'Opt return rate': best_params['return_rate'],
		'Amount used': amount_used,
		'Final amount': round(amount, 2),
		'Trades profit': n_trades_profit,
		'Trades loss': n_trades_loss,
		'Total trades': n_trades,
		'Total fees': total_fees,
		'Profits': profits,
		'Test return rate': return_rate
	}
	all_test_results.append(test_result)
	
	# Move to next window
	current_window_end += opt_window_seconds
	window_number += 1

# Print aggregate results
print("\n\n" + "=" * 80)
print("WALK-FORWARD RESULTS SUMMARY")
print("=" * 80)

if all_test_results:
	summary_df = pd.DataFrame(all_test_results)
	summary_file = f'{results_dir}/walk_forward_summary.csv'
	summary_df.to_csv(summary_file, index=None)
	
	print(f"\nTotal windows tested: {len(all_test_results)}")
	print(f"Average test return rate: {summary_df['Test return rate'].mean():.2f}%")
	print(f"Total profits across all windows: ${summary_df['Profits'].sum():.2f}")
	print(f"Total trades across all windows: {summary_df['Total trades'].sum()}")
	print(f"Total test windows with profit: {(summary_df['Test return rate'] > 0).sum()}")
	print(f"Total test windows with loss: {(summary_df['Test return rate'] < 0).sum()}")
	
	print("\nDetailed results by window:")
	print(summary_df.to_string(index=False))
	
	print(f"\n\nFull summary saved to: {summary_file}")
else:
	print("No windows were tested.")

print("\n" + "=" * 80)
