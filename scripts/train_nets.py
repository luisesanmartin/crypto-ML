import torch
import torch.optim as optim
from torch.utils.data import DataLoader
import os.path
import sys
sys.path.insert(1, './utils')
import nets
import loader
import objects
import utils_train
import matplotlib.pyplot as plt

def main():

	if torch.cuda.is_available():
		device = torch.device('cuda')
	else:
		device = torch.device('cpu')
	print('Using device: {}'.format(device))

	train_data_file = '../data/working/data_train.csv'
	validation_data_file = '../data/working/data_validation.csv'
	best_model_path = '../models/classifiers/torch-net-valleys-20260414.best.pkl'
	if os.path.isfile(best_model_path):
		model = torch.load(best_model_path)
		print('Using existing model')
	else:
		model = nets.net1().float()
		print('Using new model')
	optimizer = optim.Adam(params=model.parameters(), lr=1e-3, weight_decay=1e-4)
	dataset = loader.cryptoData()
	train_data = DataLoader(dataset, batch_size=32, shuffle=True, num_workers=15)
	epochs = 100000
	
	# Early stopping parameters
	best_val_loss = float('inf')
	patience = objects.PATIENCE  # Number of epochs with no improvement before stopping
	patience_counter = 0
	best_epoch = 0
	
	# Initialize lists for tracking losses
	epochs_list = []
	train_losses = []
	val_losses = []
	
	# Set up interactive plotting
	plt.ion()
	fig, ax = plt.subplots(figsize=(10, 6))
	
	# Training
	for epoch in range(epochs):
		losses = utils_train.train(
			train_data,
			model,
			optimizer,
			device=device,
			epoch=epoch,
			#loss_file=loss_file,
			train_data_file=train_data_file,
			test_data_file=validation_data_file,
			return_val_loss=True
			)
		
		# Unpack losses (returns tuple of train_loss, val_loss)
		train_loss = None
		val_loss = None
		if losses is not None:
			train_loss, val_loss = losses
		
		# Update loss tracking and plot every 100 epochs
		if epoch % 100 == 0 and (train_loss is not None or val_loss is not None):
			epochs_list.append(epoch)
			train_losses.append(train_loss if train_loss is not None else 0)
			val_losses.append(val_loss if val_loss is not None else 0)
			
			# Update plot
			ax.clear()
			if train_loss is not None:
				ax.plot(epochs_list, train_losses, label='Train Loss', marker='o', linewidth=2)
			if val_loss is not None:
				ax.plot(epochs_list, val_losses, label='Validation Loss', marker='s', linewidth=2)
			ax.set_xlabel('Epoch', fontsize=12)
			ax.set_ylabel('Loss', fontsize=12)
			ax.set_title('Training and Validation Loss Over Epochs', fontsize=14)
			ax.legend(fontsize=11)
			ax.grid(True, alpha=0.3)
			plt.tight_layout()
			plt.pause(0.1)
		
		# Early stopping logic: check validation loss every 100 epochs
		if epoch % 100 == 0 and val_loss is not None:
			if val_loss < best_val_loss:
				best_val_loss = val_loss
				patience_counter = 0
				best_epoch = epoch
				# Save the best model
				torch.save(model, best_model_path)
				print(f'Best model updated at epoch {epoch} with val_loss={val_loss:.5f}')
			else:
				patience_counter += 1
				print(f'No improvement for {patience_counter} evaluations. Best: epoch {best_epoch}, val_loss={best_val_loss:.5f}')
				
				if patience_counter >= patience:
					print(f'\nEarly stopping triggered at epoch {epoch}')
					print(f'   Best model was at epoch {best_epoch} with val_loss={best_val_loss:.5f}')
					# Load the best model
					model = torch.load(best_model_path)
					torch.save(model, model_path)  # Overwrite current model path with best
					print(f'   Best model restored and saved to {model_path}')
					break
	
	# Save the final plot
	plt.ioff()  # Turn off interactive mode
	plt.savefig('../data/results/loss_plot.png', dpi=300, bbox_inches='tight')
	print(f'\nLoss plot saved to ../data/results/loss_plot.png')
	plt.show()

if __name__ == '__main__':
	main()
