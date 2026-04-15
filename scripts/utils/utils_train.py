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
	train_data_file=None,
	test_data_file=None,
	return_val_loss=False):

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

	if epoch % 100 == 0 and (train_data_file or test_data_file):

		print(f'\nEpoch: {epoch}')

		train_loss = None
		val_loss = None
		
		# Training set evaluation
		if train_data_file:
			df = pd.read_csv(train_data_file)
			x_train_np = df.drop(columns=['time', 'valley']).to_numpy()
			x_train = torch.from_numpy(x_train_np).to(device=device).float()
			y_train_np = df['valley'].to_numpy()
			y_train = torch.from_numpy(y_train_np).to(device=device).float()

			# Evaluating metrics on training set
			model.eval()
			with torch.no_grad():
				y_logits = model(x_train).squeeze()
				y_score = torch.sigmoid(y_logits)
				y_pred = torch.round(y_score)
			train_loss = loss_estimation(y_logits, y_train, device).item()
			accuracy = estimate_accuracy(y_pred, y_train)
			precision = estimate_precision(y_pred, y_train)
			precision_threshold = precision_with_threshold(y_score, y_train)
			threshold2 = objects.PREDICT_THRESHOLD2
			precision_threshold2 = precision_with_threshold(y_score, y_train, threshold=threshold2)
			recall = estimate_recall(y_pred, y_train)

			print(f'\tTrain Loss: {train_loss:.5f}')
			print(f'\tTrain Precision: {precision:.5f}')
			print(f'\tTrain Precision at {objects.PREDICT_THRESHOLD:.2f} threshold: {precision_threshold:.5f}')
			print(f'\tTrain Precision at {threshold2:.2f} threshold: {precision_threshold2:.5f}')
			print(f'\tTrain Recall: {recall:.5f}')
			print(f'\tTrain Accuracy: {accuracy:.5f}')
		
		# Validation set evaluation (for early stopping)
		if test_data_file:
			df = pd.read_csv(test_data_file)
			x_test_np = df.drop(columns=['time', 'valley']).to_numpy()
			x_test = torch.from_numpy(x_test_np).to(device=device).float()
			y_test_np = df['valley'].to_numpy()
			y_test = torch.from_numpy(y_test_np).to(device=device).float()

			# Evaluating metrics on validation set
			model.eval()
			with torch.no_grad():
				y_logits = model(x_test).squeeze()
				y_score = torch.sigmoid(y_logits)
				y_pred = torch.round(y_score)
			val_loss = loss_estimation(y_logits, y_test, device).item()
			accuracy = estimate_accuracy(y_pred, y_test)
			precision = estimate_precision(y_pred, y_test)
			precision_threshold = precision_with_threshold(y_score, y_test)
			threshold2 = objects.PREDICT_THRESHOLD2
			precision_threshold2 = precision_with_threshold(y_score, y_test, threshold=threshold2)
			recall = estimate_recall(y_pred, y_test)

			print(f'\tValidation Loss: {val_loss:.5f}')
			print(f'\tValidation Precision: {precision:.5f}')
			print(f'\tValidation Precision at {objects.PREDICT_THRESHOLD:.2f} threshold: {precision_threshold:.5f}')
			print(f'\tValidation Precision at {threshold2:.2f} threshold: {precision_threshold2:.5f}')
			print(f'\tValidation Recall: {recall:.5f}')
			print(f'\tValidation Accuracy: {accuracy:.5f}')

		if return_val_loss:
			return train_loss, val_loss