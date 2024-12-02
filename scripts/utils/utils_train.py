import torch
import torch.nn as nn
import csv
import pandas as pd
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

def estimate_recall(y_pred, y_actual):

	y_pred_relevant = torch.where(y_actual == 1, y_pred, 0)
	n = torch.eq(y_actual, 1).sum().item()
	if n == 0:
		return -99
	n_correct = torch.eq(y_pred_relevant, 1).sum().item()

	return n_correct / n

def estimate_precision(y_pred, y_actual):

	y_actual_relevant = torch.where(y_pred == 1, y_actual, 0)
	n = torch.eq(y_pred, 1).sum().item()
	if n == 0:
		return -99
	n_correct = torch.eq(y_actual_relevant, 1).sum().item()

	return n_correct / n

def precision_with_threshold(y_score, y_actual, threshold=objects.PREDICT_THRESHOLD):

	y_pred = torch.where(y_score > threshold, 1, 0)
	y_actual_relevant = torch.where(y_pred == 1, y_actual, 0)
	n = torch.eq(y_pred, 1).sum().item()
	if n == 0:
		return -99
	n_correct = torch.eq(y_actual_relevant, 1).sum().item()

	return n_correct / n

def train(
	dataset,
	model,
	optimizer,
	device,
	epoch=None,
	loss_file=None,
	accuracy_file=None,
	net_file=None,
	test_data_file=None,
	test_data_file2=None):

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

	if epoch % 100 == 0 and test_data_file:

		# test set
		df = pd.read_csv(test_data_file)
		x_test_np = df.drop(columns=['time', 'valley']).to_numpy()
		x_test = torch.from_numpy(x_test_np).to(device=device).float()
		y_test_np = df['valley'].to_numpy()
		y_test = torch.from_numpy(y_test_np).to(device=device).float()

		# Evaluating accuracy (on test set)
		model.eval()
		with torch.no_grad():
			y_logits = model(x_test).squeeze()
			y_score = torch.sigmoid(y_logits)
			y_pred = torch.round(y_score)
		loss = loss_estimation(y_logits, y_test, device)
		accuracy = estimate_accuracy(y_pred, y_test)
		precision = estimate_precision(y_pred, y_test)
		precision_threshold = precision_with_threshold(y_score, y_test)
		threshold2 = 0.9
		precision_threshold2 = precision_with_threshold(y_score, y_test, threshold=threshold2)
		recall = estimate_recall(y_pred, y_test)

		print(f'\nEpoch: {epoch}')
		print(f'\tLoss: {loss:.5f}')
		print(f'\tPrecision: {precision:.5f}')
		print(f'\tPrecision at {objects.PREDICT_THRESHOLD:.2f} threshold: {precision_threshold:.5f}')
		print(f'\tPrecision at {threshold2:.2f} threshold: {precision_threshold2:.5f}')
		print(f'\tRecall: {recall:.5f}')
		print(f'\tAccuracy: {accuracy:.5f}')

		if test_data_file2:

			# test set
			df = pd.read_csv(test_data_file2)
			x_test_np = df.drop(columns=['time', 'valley']).to_numpy()
			x_test = torch.from_numpy(x_test_np).to(device=device).float()
			y_test_np = df['valley'].to_numpy()
			y_test = torch.from_numpy(y_test_np).to(device=device).float()

			# Evaluating accuracy (on test set)
			model.eval()
			with torch.no_grad():
				y_logits = model(x_test).squeeze()
				y_score = torch.sigmoid(y_logits)
				y_pred = torch.round(y_score)
			loss = loss_estimation(y_logits, y_test, device)
			accuracy = estimate_accuracy(y_pred, y_test)
			precision = estimate_precision(y_pred, y_test)
			precision_threshold = precision_with_threshold(y_score, y_test)
			precision_threshold2 = precision_with_threshold(y_score, y_test, threshold=threshold2)
			recall = estimate_recall(y_pred, y_test)

			print(f'\n\tLoss: {loss:.5f}')
			print(f'\tPrecision: {precision:.5f}')
			print(f'\tPrecision at {objects.PREDICT_THRESHOLD:.2f} threshold: {precision_threshold:.5f}')
			print(f'\tPrecision at {threshold2:.2f} threshold: {precision_threshold2:.5f}')
			print(f'\tRecall: {recall:.5f}')
			print(f'\tAccuracy: {accuracy:.5f}')


	# Saving model and loss results
	if epoch % 100 == 0 and net_file:
		torch.save(model, net_file)