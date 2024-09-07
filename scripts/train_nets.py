import torch
import torch.optim as optim
from torch.utils.data import DataLoader
import sys
sys.path.insert(1, './utils')
import nets
import loader
import utils_train

def main():

	model = nets.net1().float()
	#model = torch.load('../models/torch-net-20240623.pkl')
	#optimizer = optim.Adam(params=model.parameters(), lr=1e-2)
	#optimizer = optim.Adam(params=model.parameters(), lr=1e-3)
	#optimizer = optim.SGD(params=model.parameters(), lr=1e-3, momentum=0.9)
	optimizer = optim.Adam(params=model.parameters(), lr=0.0005)
	dataset = loader.cryptoData()
	data = DataLoader(dataset, batch_size=100, shuffle=True, num_workers=10)
	epochs = 50000
	model_path = '../models/torch-net-20240623.pkl'
	loss_file = '../data/results/loss_torch-net-20240623.csv'

	# Training
	for epoch in range(epochs):
		utils_train.train(data, model, optimizer, epoch, net_file = model_path, loss_file=loss_file)

if __name__ == '__main__':
	if torch.cuda.is_available():
		device = torch.device('cuda')
	else:
		device = torch.device('cpu')
	print('Using device: {}'.format(device))
	main()
