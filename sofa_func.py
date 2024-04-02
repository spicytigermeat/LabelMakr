import sys
sys.path.append('./SOFA')
import pathlib
import torch
import yaml
from pathlib import Path as P
from SOFA.infer import save_htk, save_textgrids, post_processing, fill_small_gaps, add_SP
from SOFA.modules import AP_detector, g2p
from SOFA.train import LitForcedAlignmentTask
import click
import lightning as pl
import textgrid
import logging

DEBUG = True

# logger setup
logger = logging.getLogger(__name__)
logging.basicConfig(format="| %(levelname)s | %(message)s | %(asctime)s |",
					datefmt="%H:%M:%S")
if DEBUG:
	logger.setLevel(logging.DEBUG)
logger.setLevel(logging.INFO)

def infer_sofa(ckpt: str,
			   dictionary: str,
			   op_format: str = 'htk',
			   matmul_bool: bool = False,
			   lang: str = 'EN',
			   g2p_bool: bool = False,
			   g2p_model: str = None,
			   g2p_cfg: str = None):

	#
	# Much of this code was referenced from "infer.py"
	# in the SOFA source code! :)
	#

	logger.info('Running SOFA inference.')

	# determine the torch device to use.
	device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

	# use tensorcores, if selected!
	if matmul_bool:
		logger.debug('Setting matmul precision to medium.')
		torch.set_float32_matmul_precision('medium')

	# set up the G2P, based on the language selected.
	if g2p_bool:
		g2p_class = getattr(g2p, "OovG2P")
		grapheme_to_phoneme = g2p_class(dictionary=dictionary, 
										g2p_model=g2p_model,
										g2p_cfg=g2p_cfg)
		logger.debug('Loaded G2p')
	else:
		g2p_class = getattr(g2p, "DictionaryG2P")
		grapheme_to_phoneme = g2p_class(dictionary=dictionary)
	grapheme_to_phoneme.set_in_format('txt')

	# set up the AP Detector
	AP_detector_class = getattr(AP_detector, 'LoudnessSpectralcentroidAPDetector')
	get_AP = AP_detector_class()

	# load up the dataset
	dataset = grapheme_to_phoneme.get_dataset(P('corpus').rglob('*.wav'))

	# load model
	torch.set_grad_enabled(False)
	model = LitForcedAlignmentTask.load_from_checkpoint(ckpt, map_location=device)
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