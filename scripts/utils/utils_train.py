import torch
import torch.nn as nn
import csv
import sys
sys.path.insert(1, './utils')
import nets
import loader
import objects

def loss_estimation(predicts, targets, device):

	loss = nn.BCEWithLogitsLoss(pos_weight=torch.FloatTensor([objects.POS_WEIGHTS])).to(device=device)
	result = loss(predicts, targets)

	return result

def estimate_accuracy(y_pred, y_actual):

	n_correct = torch.eq(y_actual, y_pred).sum().item()
	n = len(y_actual)
	result = round(n_correct / n * 100, 2)

	return n_correct / n

def estimate_precision(y_pred, y_actual):

	y_pred_relevant = torch.where(y_actual == 1, y_pred, 0)
	n = torch.eq(y_actual, 1).sum().item()
	if n == 0:
		return -99
	n_correct = torch.eq(y_pred_relevant, 1).sum().item()

	return n_correct / n

def train(dataset, model, optimizer, device, epoch=None, loss_file=None, accuracy_file=None, net_file=None):

	model = model.to(device=device)
	model.train()
	if loss_file:
		losses = []

	# Training
	for idx, (x, y) in enumerate(dataset):
		x = x.float().to(device=device)
		y = y.to(device=device)
		output = model(x).squeeze()
		loss = loss_estimation(output, y, device)

		# Backpropagation
		optimizer.zero_grad()
		loss.backward()
		optimizer.step()

		# Saving the loss
		if loss_file:
			losses.append([int(epoch), int(idx), loss.item()])

	#if loss_file:
		#with open(loss_file, 'a', newline='') as file:
			#writer = csv.writer(file)
			#for loss_row in losses:
				#writer.writerow(loss_row)

	if epoch % 10 == 0:

		# Evaluating accuracy (on training set)
		model.eval()
		with torch.no_grad():
			y_logits = model(x).squeeze()
			y_pred = torch.round(torch.sigmoid(y_logits))
		accuracy = estimate_accuracy(y_pred, y)
		precision = estimate_precision(y_pred, y)

		print(f'Epoch: {epoch}\n\tTrain loss: {loss:.5f}, train precision: {precision:.5f}, train accuracy: {accuracy:.5f}')

	# Saving model and loss results
	if epoch % 100 == 0 and net_file:
		torch.save(model, net_file)