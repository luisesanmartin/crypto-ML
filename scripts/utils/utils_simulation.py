import pandas as pd
import sys
sys.path.insert(1, './utils')
import utils_features
import objects

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

