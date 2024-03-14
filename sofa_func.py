import sys
import pathlib
import torch

def infer_sofa(ckpt, dictionary, op_format, matmul_bool, lang):
	#
	# Much of this code was referenced from "infer.py"
	# in the SOFA source code! :)
	#
	print('Running SOFA')
	sys.path.append('./SOFA')
	from SOFA.infer import save_htk, save_textgrids, post_processing, fill_small_gaps, add_SP
	from SOFA.modules import AP_detector, g2p
	from SOFA.train import LitForcedAlignmentTask
	import click
	import lightning as pl
	import textgrid

	# use tensorcores, if selected!
	if matmul_bool:
		torch.set_float32_matmul_precision('medium')

	# set up the G2P, based on the language selected.
	if lang in ['EN', 'FR']:
		g2p_class = getattr(g2p, "OovG2P")
		grapheme_to_phoneme = g2p_class(dictionary=dictionary, 
										g2p_model=f'SOFA/models/{lang.lower()}_g2p/model.ptsd',
										g2p_cfg=f'SOFA/models/{lang.lower()}_g2p/cfg.yaml')
	else:
		g2p_class = getattr(g2p, "DictionaryG2P")
		grapheme_to_phoneme = g2p_class(dictionary=dictionary)
	grapheme_to_phoneme.set_in_format('txt')

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
	try:
		predictions = trainer.predict(model, dataloaders=dataset, return_predictions=True)
	except IndexError as e:
		print(f"\nOne or more of your transcriptions are causing issues, please correct them with the transcription editor! {e}")
	try:
		predictions = get_AP.process(predictions)
	except TypeError as e:
		print(f"\n Error in one or more transcriptions, please correct them with the transcription editor!\n\n Error Code: {e}\n\n")
	predictions = post_processing(predictions)

	# output
	if op_format == 'TextGrid':
		save_textgrids(predictions)
	elif op_format == 'htk':
		save_htk(predictions)

if __name__ == "__main__":
	print("What u doin silly!")