import sys
sys.path.append('.')
from ftfy import fix_text as fxy
import subprocess
import re
import glob
#from dp.phonemizer import Phonemizer

class Transcriber(object):
	def __init__(self, lang, wh_model):
		super().__init__()
		import whisper
		from whisper.tokenizer import get_tokenizer

		# referenced code from MLo7's MFA Notebook :)
		self.model = whisper.load_model(wh_model)
		whisper.DecodingOptions(language=lang.lower())
		self.tokenizer = get_tokenizer(multilingual=True)
		self.number_tokens = [i for i in range(self.tokenizer.eot) if all(c in "0123456789" for c in self.tokenizer.decode([i]))]

	def jpn_g2p(self, jpn):
		# uses .exe version of openjtalk G2p
		phonemes = subprocess.check_output(f"g2p-jp/japanese_g2p.exe -rs {jpn}", shell=False)
		g2p_op = str(phonemes)
		fixed = re.sub(r"([aeiouAIEOUN])", r" \1 ", g2p_op[2:-5])
		# fix cl
		fixed = re.sub("cl", "cl ", fixed)
		# remove punctuation
		fixed = re.sub(r"[.!?,]", "", fixed)
		# remove extra spaces
		fixed = re.sub(" {2,}", " ", fixed)
		fixed = re.sub("A", "a", fixed)
		fixed = re.sub("I", "i", fixed)
		fixed = re.sub("U", "u", fixed)
		fixed = re.sub("E", "e", fixed)
		fixed = re.sub("O", "o", fixed)
		return fixed

	'''
	# working on this in the next update B)
	def eng_g2p(self, eng_str):
		pmz = Phonemizer.from_checkpoint('models/en_us_cmudict_ipa_forward.pt')
		print(pmz("butter", lang='en_us'))
	'''

	def run_transcription(self, lang):
		try:
			for file in glob.glob('corpus/**/*.wav', recursive=True):
				out_name = file[:-4] + '.lab'

				answer = self.model.transcribe(file, suppress_tokens=[-1] + self.number_tokens)
				if lang.upper() == "JP":
					trns_str_kanji = fxy(answer['text'])
					trns_str = self.jpn_g2p(trns_str_kanji)
				else:
					trns_str = fxy(answer['text']).lower()
				trns_str = re.sub(r"[.,!?]", "", trns_str)

				with open(out_name, 'w+', encoding='utf-8') as whis:
					whis.write(trns_str)
					whis.close()

				print(f"Wrote transcription for {file} in corpus.")

		except RuntimeError as e:
			print(f"Error Transcribing: {e}")

if __name__ == "__main__":
	#Transcriber.eng_g2p(Transcriber, 'test')
	print('What do u think ur doing silly billy!')