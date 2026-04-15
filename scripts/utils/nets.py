import torch
import torch.nn as nn

class net1(nn.Module):
	def __init__(self):
		super(net1, self).__init__()
		if torch.cuda.is_available():
			device = torch.device('cuda')
		else:
			device = torch.device('cpu')
		self.linear1 = nn.Linear(55, 32)
		self.linear2 = nn.Linear(32, 16)
		self.linear3 = nn.Linear(16, 8)
		self.linear4 = nn.Linear(8, 1)
		self.relu = nn.ReLU()
		self.dropout = nn.Dropout(p=0.5)

	def forward(self, x):
		x = self.dropout(self.relu(self.linear1(x)))
		x = self.dropout(self.relu(self.linear2(x)))
		x = self.dropout(self.relu(self.linear3(x)))
		x = self.linear4(x)
		return x