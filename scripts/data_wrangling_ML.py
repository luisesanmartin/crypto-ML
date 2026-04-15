import pickle
import sys
sys.path.insert(1, './utils')
import utils_data

###############
## Load data ##
###############

print("1: Reading data...")

file = '../data/raw/bitstamp/data_dogeusd_2025-01-01_2026-03-29_step60.pkl'
with open(file, 'rb') as f:
	data = pickle.load(f)
data_dic = utils_data.make_data_dic(data)

###############
## Variables ##
###############

print("2: Creating variables...")
df_train, df_validation = utils_data.make_data_train_test(data_dic)

# Exporting
print('3: Saving dataframes...')
file = '../data/working/data_train.csv'
df_train.to_csv(file, index=False)
file = '../data/working/data_validation.csv'
df_validation.to_csv(file, index=False)