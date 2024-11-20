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

file_validation = '../data/raw/data_BITSTAMP_SPOT_BTC_USD_10MIN_2024-09-07T20:10:00_2024-11-19T23:00:00.pkl'
with open(file_validation, 'rb') as f:
	data_validation = pickle.load(f)
data_dic_validation = utils_data.make_data_dic(data_validation)

###############
## Variables ##
###############

print("2: Creating variables...")
df_train, df_test = utils_data.make_data_train_test(data_dic)
df_validation = utils_data.make_data_validation(data_dic_validation)

# Exporting
print('3: Saving dataframes...')
file = '../data/working/data_train.csv'
df_train.to_csv(file, index=False)
file = '../data/working/data_test.csv'
df_test.to_csv(file, index=False)
file = '../data/working/data_validation.csv'
df_validation.to_csv(file, index=False)