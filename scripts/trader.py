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
	
	# Variables for tracking results
	hold = 0
	profits_total = 0

	# Logging in
	#login = trading_utils.login()

	while True:

		minutes, seconds = time_utils.minute_seconds_now()
		if (minutes + 1) % 10 == 0 and seconds >= 58: # 9m, >=58s
			time_now = time_utils.time_in_string(datetime.now())
			print('\nIts {}'.format(time_now))
			print('Starting now...')
			
			# Data
			data = fetch_utils.get_data_min()
			data_dic = data_utils.make_data_dic(data)
			X = data_utils.make_x_predict(data_dic)
			current_price = data[0]['price_close']
			print('Current price (API): {}'.format(current_price))

			# Prediction
			prediction = data_utils.prediction_from_net(X, model)

			# Trader in action
			if hold == 0:
				print('Currently not holding...')
				if prediction == 1:
					crypto_quantity = round(amount / current_price, 8)
					#buy_order = trading_utils.buy_crypto(crypto=crypto, usd_amount=amount)
					buy_order = trading_utils.bs_buy_limit_order(amount=crypto_quantity,
															 price=current_price,
															 market_symbol=market_symbol)
					print(buy_order.content)
					buy_order = buy_order.json()
					amount_spent = float(crypto_quantity) * float(buy_order['price'])
					order_type = buy_order['type']
					print('Sent a limit order to buy '+str(crypto_quantity)+' for $'+str(round(amount_spent, 2)))
					print('Current price: {}'.format(buy_order['price']))
					hold = 1
				elif prediction == 0:
					print('Price is predicted to decrease, not buying')
					pass
			
			elif hold == 1:
				print('Currently holding crypto...')
				if prediction == 0:
					#sell_order = trading_utils.sell_crypto(crypto=crypto, crypto_amount=float(crypto_quantity))
					sell_order = trading_utils.bs_sell_limit_order(amount=crypto_quantity,
																price=current_price,
																market_symbol=market_symbol)
					print(sell_order.content)
					sell_order = sell_order.json()
					try:
						amount_sold = float(crypto_quantity) * float(sell_order['price'])
					except KeyError:
						print(sell_order)
						raise KeyError
					profits = amount_sold - amount_spent
					profits_total += profits
					amount = amount_sold
					print('Sent a limit order to sell '+str(crypto_quantity)+' for $'+str(round(amount_sold, 2)))
					print('Current price: {}'.format(sell_order['price']))
					print('Profits with this operation: $'+str(round(profits, 2)))
					print('Total profits: $'+str(round(profits_total, 2)))
					hold = 0
				elif prediction == 1:
					print('Price is predicted to increase, not selling')
					pass

			time.sleep(550)

		time.sleep(1)

if __name__ == '__main__':
	main()