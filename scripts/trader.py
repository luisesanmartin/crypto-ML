import sys
sys.path.insert(1, './utils')
import utils_time as time_utils
import utils_fetch as fetch_utils
import utils_data as data_utils
import utils_trade as trading_utils
import utils_features
from datetime import datetime
import time
import torch
import objects

def main():

	# Loading model
	#model_path = '../models/classifiers/torch-net-valleys-20241118.pkl'
	#model = torch.load(model_path)
	#model.eval()
	#model.to('cpu')

	# Globals and variables
	market_symbol = 'btcusd'
	amount = 75
	margin = objects.MARGIN # same as sell rate in simulation
	fee_rate = objects.FEE_RATE
	buy_rate = objects.BUY_RATE
	cut_loss_rate = objects.CUT_LOSS_RATE
	periods = objects.PERIOD
	#threshold = objects.PREDICT_THRESHOLD
	
	# Variables for tracking results
	hold = 0
	profits_total = 0
	#periods = 0
	#periods_holding = 0
	#correct_predictions = 0
	#predictions = []
	#prices = []
	#periods_to_hold = objects.VALLEY_PERIODS + 12

	while True:

		minutes, seconds = time_utils.minute_seconds_now()

		data = fetch_utils.get_data_min()
		if (minutes + 1) % 10 == 0 and seconds >= 59: # 9m, 59s
			time_now = time_utils.time_in_string(datetime.now())
			print('\nIts {}'.format(time_now))
			
			# Data
			data = fetch_utils.get_data_min()
			data_dic = data_utils.make_data_dic(data)
			#X = data_utils.make_x_predict(data_dic)
			current_price = data[0]['price_close']
			#prices.append(current_price)
			print('Current price (API): {}'.format(current_price))

			# Prediction
			#prediction = data_utils.prediction_from_net(X, model, threshold=threshold)
			#predictions.append(prediction)

			# Trader in action
			if hold == 0:
				print('Currently not holding...')

				current_time = data[0]['time_period_end'].split('.')[0]
				print(current_time)
				avg_price = utils_features.avg_price(data_dic, periods, current_time)
				print(avg_price)

				if float(current_price) < avg_price * (1-buy_rate):

					print('Valley detected!')
					crypto_quantity = round(amount / current_price, 8)
					buy_order = trading_utils.bs_buy_limit_order(amount=crypto_quantity,
															 price=current_price,
															 market_symbol=market_symbol)
					buy_order = buy_order.json()
					try:
						price_buy = float(buy_order['price'])
					except KeyError:
						print(buy_order)
						raise KeyError
					amount_spent = float(crypto_quantity) * price_buy
					fee = amount_spent * fee_rate
					profits_total -= fee
					print('Sent a limit order to buy '+str(crypto_quantity)+' for $'+str(round(amount_spent, 2)))
					print('Purchase price: {}'.format(price_buy))
					hold = 1
					#periods_holding = 0
				else:
					print('No valley detected, not buying')
					pass
			
			elif hold == 1:
				#periods_holding += 1
				print('Currently holding crypto...')

				# We only sell if current price is higher than the
				# last buy price by the amount in "margin"
				price_with_margin = price_buy * (1 + margin) 
				
				if current_price > price_buy * (1+buy_rate) or \
		   		   current_price < price_buy * (1-cut_loss_rate):

					sell_order = trading_utils.bs_sell_limit_order(amount=crypto_quantity,
																price=current_price,
																market_symbol=market_symbol)
					sell_order = sell_order.json()
					try:
						amount_sold = float(crypto_quantity) * float(sell_order['price'])
					except KeyError:
						print(sell_order)
						raise KeyError
					fee = amount_sold * fee_rate
					profits_total -= fee
					profits = amount_sold - amount_spent
					profits_total += profits
					amount = amount_sold
					#if not current_price > price_buy * (1 + margin):
						#print("Selling because we've reached the valley periods...")
					print('Sent a limit order to sell '+str(crypto_quantity)+' for $'+str(round(amount_sold, 2)))
					print('Sell price: {}'.format(sell_order['price']))
					print('Profits with this operation: $'+str(round(profits, 2)))
					hold = 0
				else:
					print("Price is not yet higher than the desired margin")
					print('Last purchase price: ${}'.format(price_buy))
					print('Price with margin: ${}'.format(round(price_with_margin)))

			# Accuracy tracking:
			#periods += 1
			#print('Total periods: {}'.format(periods))
			#print('Total profits: $'+str(round(profits_total, 2)))
			time.sleep(550)

		time.sleep(0.5)

if __name__ == '__main__':
	main()