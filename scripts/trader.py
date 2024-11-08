import sys
sys.path.insert(1, './utils')
import utils_time as time_utils
import utils_fetch as fetch_utils
import utils_data as data_utils
import utils_trade as trading_utils
from datetime import datetime
import time
import torch

def main():

	# Loading model
	model_path = '../models/classifiers/torch-net-20240623.pkl'
	model = torch.load(model_path)
	model.eval()
	model.to('cpu')

	# Globals and variables
	market_symbol = 'btcusd'
	amount = 90
	margin = 0.008 # 0.4% is the fee for buying and selling in BS
	fee_rate = 0.004
	price_wander_wait = 4 # hours we want to wait after making a sell
	buy_offer = 0.9995
	
	# Variables for tracking results
	hold = 0
	profits_total = 0
	periods = 0
	correct_predictions = 0
	predictions = []
	prices = []
	sell = False

	while True:

		minutes, seconds = time_utils.minute_seconds_now()
		if (minutes + 1) % 10 == 0 and seconds >= 59: # 9m, 59s
			time_now = time_utils.time_in_string(datetime.now())
			print('\nIts {}'.format(time_now))
			print('Starting now...')
			
			# Data
			data = fetch_utils.get_data_min()
			data_dic = data_utils.make_data_dic(data)
			X = data_utils.make_x_predict(data_dic)
			current_price = data[0]['price_close']
			prices.append(current_price)
			print('Current price (API): {}'.format(current_price))

			# Prediction
			prediction = data_utils.prediction_from_net(X, model)
			predictions.append(prediction)

			# Trader in action
			if hold == 0:
				print('Currently not holding...')
				
				if prediction == 1:
					#price_buy = round(current_price * buy_offer)
					#crypto_quantity = round(amount / price_buy, 8)
					crypto_quantity = round(amount / current_price, 8)
					buy_order = trading_utils.bs_buy_limit_order(amount=crypto_quantity,
															 #price=price_buy,
															 price=current_price,
															 market_symbol=market_symbol)
					buy_order = buy_order.json()
					price_buy = float(buy_order['price'])
					amount_spent = float(crypto_quantity) * price_buy
					fee = amount_spent * fee_rate
					profits_total -= fee
					print('Sent a limit order to buy '+str(crypto_quantity)+' for $'+str(round(amount_spent, 2)))
					print('Purchase price: {}'.format(price_buy))
					hold = 1
				else:
					print('Price is predicted to decrease, not buying')
					pass
			
			elif hold == 1:
				print('Currently holding crypto...')

				# We only sell if price is predicted to decrease (prediction == 0)
				# and current price is higher than the last buy price by the amount in "margin"
				if prediction == 0:
					if current_price > price_buy * (1 + margin):
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
						print('Sent a limit order to sell '+str(crypto_quantity)+' for $'+str(round(amount_sold, 2)))
						print('Sell price: {}'.format(sell_order['price']))
						print('Profits with this operation: $'+str(round(profits, 2)))
						#print('Total profits: $'+str(round(profits_total, 2)))
						hold = 0
						sell = True
					else:
						print("Price is predicted to decrease but it's not higher than the desired margin")
						print('Last purchase price: ${}'.format(price_buy))
				else:
					print('Price is predicted to increase, not selling')
					pass

			# Accuracy tracking:
			periods += 1
			print('Total periods: {}'.format(periods))
			if periods > 1:
				last_prediction = predictions[-2]
				true_movement = int(prices[-1] > prices[-2])
				if last_prediction == true_movement:
					correct_predictions += 1
				print('Accuracy: {}%'.format(round(correct_predictions/(periods-1)*100)))
			print('Total profits: $'+str(round(profits_total, 2)))
			if sell:
				time.sleep(60*60*price_wander_wait) # let the price wander for a few hours
				sell = False
			else:
				time.sleep(550)

		time.sleep(0.5)

if __name__ == '__main__':
	main()