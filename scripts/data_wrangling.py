import pickle
import sys
sys.path.insert(1, './utils')
import utils_data

###############
## Load data ##
###############

print("1: Reading data...")

file = '../data/raw/data_10MIN_2024-06-21T00:10:00_2022-07-27T13:50:00.pkl'
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
df = utils_data.make_x_train(data_dic)

# Exporting
print('3: Saving dataframe...')
file = '../data/working/data.csv'
df.to_csv(file, index=False)
