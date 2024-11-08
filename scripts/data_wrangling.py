import pickle
import sys
sys.path.insert(1, './utils')
import utils_data

###############
## Load data ##
###############

print("1: Reading data...")

file = '../data/raw/data_BITSTAMP_SPOT_BTC_USD_10MIN_2022-10-14T09:30:00_2024-09-07T20:00:00.pkl'
with open(file, 'rb') as f:
	data = pickle.load(f)

data_dic = utils_data.make_data_dic(data)

######################
## Sample selection ##
######################

# To add

###############
## Variables ##
###############

print("2: Creating variables...")
df = utils_data.make_data_train(data_dic)

# Exporting
print('3: Saving dataframe...')
file = '../data/working/data.csv'
df.to_csv(file, index=False)
