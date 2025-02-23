import sys
sys.path.insert(1, './utils')
import utils_time as time_utils
import utils_fetch as fetch_utils
import utils_trade as trading_utils
import utils_features
from datetime import datetime
import time
import objects

def main():

	# Globals and variables
	market_symbol = 'btcusd'
	amount = 100
	fee_rate = objects.FEE_RATE
	buy_rate = objects.BUY_RATE
	cut_loss_rate = objects.CUT_LOSS_RATE
	periods = objects.PERIOD
	
	# Variables for tracking results
	hold = 0
	profits_total = 0
	periods_run = 0

	# Others
	sender, to, key = trading_utils.email_credentials()

	while True:

		minutes, seconds = time_utils.minute_seconds_now()

		if (minutes + 1) % 10 == 0 and seconds >= 59: # 9m, 59s
			time_now = time_utils.time_in_string(datetime.now())
			print('\nIts {}'.format(time_now))
			
			# Data
			try:
				#data = fetch_utils.get_data_min()
				data = fetch_utils.get_data_bitstamp()
			except TypeError:
				continue
			#current_price = data[0]['price_close']
			current_price = int(data[-1]['close'])
			print('Current price (API): {}'.format(current_price))

			# Trader in action
			if hold == 0:
				print('Currently not holding...')

				#current_time = data[0]['time_period_end'].split('.')[0]
				#avg_price = utils_features.avg_price(data_dic, periods, current_time)
				avg_price = utils_features.avg_price_bistamp(data)
				print('Valley price: {}'.format(round(avg_price * (1-buy_rate))))

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
						subject = 'Trader bot - Trader stopped'
						message = f'See buy order below:\n{buy_order}'
						trading_utils.send_email(message, subject, sender, to, key)
						raise KeyError
					amount_spent = float(crypto_quantity) * price_buy
					fee = amount_spent * fee_rate
					profits_total -= fee
					line1 = 'Sent a limit order to buy '+str(crypto_quantity)+' for $'+str(round(amount_spent, 2))
					print(line1)
					line2 = 'Purchase price: {}'.format(price_buy)
					print(line2)
					hold = 1
					subject = 'Trader bot - Valley detected'
					message = f'Valley detected!\n{line1}\n{line2}'
					trading_utils.send_email(message, subject, sender, to, key)
				else:
					print('No valley detected, not buying')
					pass
			
			elif hold == 1:
				print('Currently holding crypto...')

				# We only sell if current price is higher than the
				# last buy price by the amount in "margin"
				price_with_margin = price_buy * (1 + buy_rate) 
				
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
						subject = 'Trader bot - Trader stopped'
						message = f'See sell order below:\n{buy_order}'
						trading_utils.send_email(message, subject, sender, to, key)
						raise KeyError
					fee = amount_sold * fee_rate
					profits_total -= fee
					profits = amount_sold - amount_spent
					profits_total += profits
					amount = amount_sold
					line1 = 'Sent a limit order to sell '+str(crypto_quantity)+' for $'+str(round(amount_sold, 2))
					print(line1)
					line2 = 'Sell price: {}'.format(sell_order['price'])
					print(line2)
					line3 = 'Profits with this operation (without fee): $'+str(round(profits, 2))
					print(line3)
					hold = 0
					subject = 'Trader bot - Sell order'
					message = f'{line1}\n{line2}\n{line3}'
					trading_utils.send_email(message, subject, sender, to, key)
				else:
					print("Price is not yet higher than the desired margin")
					print('Last purchase price: ${}'.format(price_buy))
					print('Price with margin: ${}'.format(round(price_with_margin)))

			# Accuracy tracking:
			periods_run += 1
			print('Total periods: {}'.format(periods_run))
			print('Total profits: $'+str(round(profits_total, 2)))
			time.sleep(550)

		time.sleep(0.5)

if __name__ == '__main__':
	main()