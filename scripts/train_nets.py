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

	train_data_file = '../data/working/data_train.csv'
	validation_data_file = '../data/working/data_validation.csv'
	model_path = '../models/classifiers/torch-net-valleys-20260414.pkl'
	best_model_path = '../models/classifiers/torch-net-valleys-20260414.best.pkl'
	if os.path.isfile(model_path):
		model = torch.load(model_path)
		print('Using existing model')
	else:
		model = nets.net1().float()
		print('Using new model')
	optimizer = optim.Adam(params=model.parameters(), lr=1e-3, weight_decay=1e-4)
	dataset = loader.cryptoData()
	train_data = DataLoader(dataset, batch_size=32, shuffle=True, num_workers=12)
	epochs = 100000
	
	# Early stopping parameters
	best_val_loss = float('inf')
	patience = 30  # Number of epochs with no improvement before stopping
	patience_counter = 0
	best_epoch = 0
	
	# Training
	for epoch in range(epochs):
		val_loss = utils_train.train(
			train_data,
			model,
			optimizer,
			device=device,
			epoch=epoch,
			net_file = model_path,
			#loss_file=loss_file,
			test_data_file=validation_data_file,
			return_val_loss=True
			)
		
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

if __name__ == '__main__':
	main()
