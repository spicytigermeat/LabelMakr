import sys
import pathlib

def infer_sofa(ckpt, dictionary, op_format):
	print('Running SOFA')
	sys.path.append('./SOFA')
	from SOFA.infer import save_htk, save_textgrids, post_processing, fill_small_gaps, add_SP
	from SOFA.modules import AP_detector, g2p
	from SOFA.train import LitForcedAlignmentTask
	import click
	import lightning as pl
	import textgrid
	import torch

	# set up the G2P, which currently is just a dictionary
	g2p_class = getattr(g2p, "DictionaryG2P")
	grapheme_to_phoneme = g2p_class(dictionary=dictionary)

	# set up the AP Detector
	AP_detector_class = getattr(AP_detector, 'LoudnessSpectralcentroidAPDetector')
	get_AP = AP_detector_class()

	# load up the dataset
	dataset = grapheme_to_phoneme.get_dataset(pathlib.Path('corpus').rglob('*.wav'))

	# load model
	torch.set_grad_enabled(False)
	model = LitForcedAlignmentTask.load_from_checkpoint(ckpt)
	model.set_inference_mode('force')
	trainer = pl.Trainer(logger=False)

	# run predictions
	predictions = trainer.predict(model, dataloaders=dataset, return_predictions=True)
	predictions = get_AP.process(predictions)
	predictions = post_processing(predictions)

	# output
	if op_format == 'TextGrid':
		save_textgrids(predictions)
	elif op_format == 'htk':
		save_htk(predictions)

if __name__ == "__main__":
	print("What u doin silly!")