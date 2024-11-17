import torch
import torch.optim as optim
from torch.utils.data import DataLoader
import os.path
import sys
sys.path.insert(1, './utils')
import nets
import loader
import utils_train

def main():

	if torch.cuda.is_available():
		device = torch.device('cuda')
	else:
		device = torch.device('cpu')
	print('Using device: {}'.format(device))

	test_data_file = '../data/working/data_test.csv'
	model_path = '../models/classifiers/torch-net-valleys-20241111.pkl'
	if os.path.isfile(model_path):
		model = torch.load(model_path)
		print('Using existing model')
	else:
		model = nets.net1().float()
		print('Using new model')
	optimizer = optim.SGD(params=model.parameters(), lr=0.0005, momentum=0.9)
	#optimizer = optim.Adam(params=model.parameters(), lr=0.1e-4)
	dataset = loader.cryptoData()
	train_data = DataLoader(dataset, batch_size=32, shuffle=True, num_workers=15)
	epochs = 100000
	#loss_file = '../data/results/loss_torch-net-20241108.csv'

	# Training
	for epoch in range(epochs):
		utils_train.train(
			train_data,
			model,
			optimizer,
			device=device,
			epoch=epoch,
			net_file = model_path,
			#loss_file=loss_file,
			test_data_file=test_data_file
			)

if __name__ == '__main__':
	main()
