import pandas as pd
import os
import sys
sys.path.insert(1, './utils')
import utils_features
import objects

def simulate_one_symbols(
	data_dic,
	time,
	hold,
	amount,
	crypto,
	total_fees,
	n_trades_profit,
	n_trades_loss,
	n_trades,
	last_purchase_price,
	periods,
	buy_rate,
	sell_rate,
	cut_loss_rate,
	symbol_holding
	):

	symbols = objects.BITSTAMP_SYMBOLS
	current_prices = {symbol: float(data_dic[time][symbol]['close']) for symbol in symbols}

	if not hold:

		avg_prices = {symbol: utils_features.avg_price_symbol_periods(data_dic, symbol, periods, time) for symbol in symbols}

		for symbol in symbols:

			current_price = current_prices[symbol]
			avg_price = avg_prices[symbol]

			if buy_rate < 0:
				
				if current_price < avg_price * (1+buy_rate):

					hold = True
					crypto = amount / current_price
					fee = amount * objects.FEE_RATE
					amount = 0			
					total_fees += fee
					last_purchase_price = current_price
					symbol_holding = symbol

					return hold, crypto, amount, total_fees, last_purchase_price, symbol_holding, n_trades_profit, n_trades_loss, n_trades

			else: # buy_rate > 0

				if current_price > avg_price * (1+buy_rate):

					hold = True
					crypto = amount / current_price
					fee = amount * objects.FEE_RATE
					amount = 0			
					total_fees += fee
					last_purchase_price = current_price
					symbol_holding = symbol

					return hold, crypto, amount, total_fees, last_purchase_price, symbol_holding, n_trades_profit, n_trades_loss, n_trades

	elif hold:

		current_price = current_prices[symbol_holding]

		if current_price > last_purchase_price * (1+sell_rate) or \
		   current_price < last_purchase_price * (1-cut_loss_rate):

			hold = False
			amount = crypto * current_price
			fee = amount * objects.FEE_RATE
			crypto = 0
			total_fees += fee
			symbol_holding = None
			n_trades += 1

			if current_price > last_purchase_price * (1+sell_rate):
				n_trades_profit += 1
			elif current_price < last_purchase_price * (1-cut_loss_rate):
				n_trades_loss += 1

	return hold, crypto, amount, total_fees, last_purchase_price, symbol_holding, n_trades_profit, n_trades_loss, n_trades

def simulate_all_symbols(
	data_dic,
	results_file,
	detailed_results_path,
	amount_to_trade,
	symbols = objects.BITSTAMP_SYMBOLS,
	periods=objects.PERIODS,
	buy_rates=objects.BUY_RATES,
	sell_rates=objects.SELL_RATES,
	cut_loss_rates=objects.CUT_LOSS_RATES):

	'''
	periods: list of periods to use for the avg price estimation
	buy_rates: list of rates different than the avg that activate a purchase
	sell_rates: list of rates above purchase price at which to sell
	cut_loss_rates: list of rates to cut losses
	'''

	times = list(data_dic.keys())
	times.sort()
	results = []
	cols = [
		'Periods', 
		'Buy rate', 
		'Sell rate', 
		'Cut loss rate', 
		'Amount used', 
		'Final amount',
		'Number of trades with profit',
		'Number of trades with loss',
		'Number of trades',
		'Total fees', 
		'Profits',
		'Return rate']
	cols2 = [
		'Time',
		'Amount',
		'Total fees',
		'N trades-profit',
		'N trades-loss',
		'N trades',
		'Symbol holding']

	for period in periods:
		for buy_rate in buy_rates:
			for sell_rate in sell_rates:
				for cut_loss_rate in cut_loss_rates:

					results_combination = []
					hold = False
					amount = amount_to_trade
					crypto = 0
					total_fees = 0
					n_trades_profit = 0
					n_trades_loss = 0
					n_trades = 0
					last_purchase_price = None
					symbol_holding = None

					for time in times[period:]:

						results_combination.append([time, amount, total_fees, n_trades_profit, n_trades_loss, n_trades, symbol_holding])
						hold, crypto, amount, total_fees, last_purchase_price, symbol_holding, n_trades_profit, n_trades_loss, n_trades = \
							simulate_one_symbols(
								data_dic,
								time,
								hold,
								amount,
								crypto,
								total_fees,
								n_trades_profit,
								n_trades_loss,
								n_trades,
								last_purchase_price,
								period,
								buy_rate,
								sell_rate,
								cut_loss_rate,
								symbol_holding)

					df = pd.DataFrame(columns=cols2, data=results_combination)
					detailed_results_file = f'{detailed_results_path}/period{period}-buy_rate{buy_rate}-sell_rate{sell_rate}-cut_loss_rate{cut_loss_rate}.csv'
					df.to_csv(detailed_results_file, index=None)
					
					# Estimating finals
					if hold: # then we sell
						current_price = float(data_dic[time][symbol_holding]['close'])
						amount = crypto * current_price
						fee = amount * objects.FEE_RATE
						total_fees += fee

					amount_used = round(amount_to_trade+total_fees, 2)
					profits = round(amount - amount_used, 2)
					return_rate = (profits / amount_used ) * 100
					amount = round(amount, 2)
					total_fees = round(total_fees, 2)

					print('Periods        : {}'.format(period))
					print('Buy rate       : {}'.format(buy_rate))
					print('Sell rate      : {}'.format(sell_rate))
					print('Cut loss rate  : {}'.format(cut_loss_rate))
					print('Amount used    : {}'.format(amount_to_trade+total_fees))
					print('Final amount   : {}'.format(amount))
					print(f'N trades-profit: {n_trades_profit}')
					print(f'N trades-loss  : {n_trades_loss}')
					print('N trades       : {}'.format(n_trades))
					print('Total fees     : {}'.format(total_fees))
					print('\t\tProfits: {}'.format(profits))
					print('\t\tReturn : {}%'.format(round(return_rate, 1)))
					results.append([
						period,
						buy_rate,
						sell_rate,
						cut_loss_rate,
						amount_used,
						amount,
						n_trades_profit,
						n_trades_loss,
						n_trades,
						total_fees,
						profits,
						return_rate])

	df = pd.DataFrame(columns=cols, data=results)
	df.to_csv(results_file, index=None)

	return True

def simulate_one(
	data_dic,
	time,
	hold,
	amount,
	crypto,
	total_fees,
	last_purchase_price,
	periods,
	buy_rate,
	sell_rate,
	cut_loss_rate
	):

	current_price = data_dic[time]['price_close']

	if not hold:

		avg_price = utils_features.avg_price(data_dic, periods, time)

		if current_price < avg_price * (1-buy_rate):

			hold = True
			crypto = amount / current_price
			fee = amount * objects.FEE_RATE
			amount = 0			
			total_fees += fee
			last_purchase_price = current_price

	elif hold:

		if current_price > last_purchase_price * (1+buy_rate) or \
		   current_price < last_purchase_price * (1-cut_loss_rate):

		   hold = False
		   amount = crypto * current_price
		   fee = amount * objects.FEE_RATE
		   crypto = 0
		   total_fees += fee

	return hold, crypto, amount, total_fees, last_purchase_price

def simulate_all(
	data_dic,
	results_file,
	amount_to_trade,
	periods=objects.PERIODS,
	buy_rates=objects.BUY_RATES,
	sell_rates=objects.SELL_RATES,
	cut_loss_rates=objects.CUT_LOSS_RATES):

	'''
	periods: list of periods to use for the avg price estimation
	buy_rates: list of rates below the avg that activate a purchase
	sell_rates: list of rates above purchase price at which to sell
	cut_loss_rates: list of rates to cut losses
	'''

	times = list(data_dic.keys())
	times.sort()
	results = []

	for period in periods:
		for buy_rate in buy_rates:
			for sell_rate in sell_rates:
				for cut_loss_rate in cut_loss_rates:

					hold = False
					amount = amount_to_trade
					crypto = 0
					total_fees = 0
					profits = 0
					last_purchase_price = None

					for time in times[period-1:]:

						hold, crypto, amount, total_fees, last_purchase_price = \
							simulate_one(
								data_dic,
								time,
								hold,
								amount,
								crypto,
								total_fees,
								last_purchase_price,
								period,
								buy_rate,
								sell_rate,
								cut_loss_rate)

					# Estimating finals
					current_price = data_dic[time]['price_close']
					if hold: # then we sell
						amount = crypto * current_price
						fee = amount * objects.FEE_RATE
						total_fees += fee

					amount_used = round(amount_to_trade+total_fees, 2)
					profits = round(amount - amount_used, 2)
					return_rate = (profits / amount_used ) * 100
					amount = round(amount, 2)
					total_fees = round(total_fees, 2)

					print('Periods      : {}'.format(period))
					print('Buy rate     : {}'.format(buy_rate))
					print('Sell rate    : {}'.format(sell_rate))
					print('Cut loss rate: {}'.format(cut_loss_rate))
					print('Amount used  : {}'.format(amount_to_trade+total_fees))
					print('Final amount : {}'.format(amount))
					print('Total fees   : {}'.format(total_fees))
					print('\t\tProfits: {}'.format(profits))
					print('\t\tReturn : {}%'.format(round(return_rate, 1)))
					results.append([
						period, 
						buy_rate, 
						sell_rate, 
						cut_loss_rate, 
						amount_used, 
						amount, 
						total_fees, 
						profits, 
						return_rate])

	cols = [
		'Periods', 
		'Buy rate', 
		'Sell rate', 
		'Cut loss rate', 
		'Amount used', 
		'Final amount',
		'Total fees', 
		'Profits',
		'Return']
	df = pd.DataFrame(columns=cols, data=results)
	df.to_csv(results_file, index=None)

	return None
