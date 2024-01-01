# general stuff
import os, sys, re, glob
# GUI stuff
import customtkinter as ctk
import tkinter as tk
from ftfy import fix_text as fxy # unicode text all around fix
import threading
# function stuff
import yaml
import pathlib
import warnings
#import pykakasi # japanese language processing

warnings.filterwarnings("ignore")
sys.path.append('.')

# default stuff configurations :)
ctk.set_appearance_mode("System")
ctk.set_default_color_theme('assets/ctk_tgm_theme.json')
ctk.deactivate_automatic_dpi_awareness()

class Transcriber:
	def __init__(self, lang, wh_model):
		super().__init__()
		import whisper
		from whisper.tokenizer import get_tokenizer

		# referenced code from MLo7's MFA Notebook :)
		self.model = whisper.load_model(wh_model)
		whisper.DecodingOptions(language=lang.lower())
		self.tokenizer = get_tokenizer(multilingual=True)
		self.number_tokens = [i for i in range(self.tokenizer.eot) if all(c in "0123456789" for c in self.tokenizer.decode([i]))]

	def conv_kana2roma(self, string):
		# i have no idea how i want to implement this yet lol
		#kks = pykakasi.kakasi():
		#kks.setMode("J", "H")
		#kks.setMode("K", "H")
		#jpconv = kks.getConverter()
		return 0

	def run_transcription(self, audio):
		answer = self.model.transcribe(audio, suppress_tokens=[-1] + self.number_tokens)
		if lang == "JP":
			trns_str = fxy(self.conv_kana2roma(answer['text']))
		else:
			trns_str = fxy(answer['text'])
		print(f"Wrote transcription for {audio} in corpus.")
		return trns_str

class App(ctk.CTk):
	def __init__(self):
		super().__init__()

		def cmbo_callback(choice):
			print('selected option:', choice)

		def whisper_function(self):
			self.prog_bar.start()
			trnsr = Transcriber(self.trans_lang_choice.get(), self.inf_wh_model.get())
			try:
				for file in glob.glob('corpus/**/*.wav', recursive=True):
					answer = ''
					out_name = file[:-4] + '.lab'
					trns_str = trnsr.run_transcription(file)
					output = fxy(trns_str.lower())
					final_op = re.sub(r"[.,!?]", "", output)
					with open(out_name, 'w+', encoding='utf-8') as whis:
						whis.write(final_op)
						whis.close()
				self.prog_bar.stop()
				self.prog_bar.set(0)
			except RuntimeError as e:
				print(f"Error Transcribing: {e}")
				self.prog_bar.stop()
				self.prog_bar.set(0)

		def run_transcriber(self):
			# initialize the whisper transcriber class
			print("Initializing Whisper")
			# get a list of each file path needing transcription
			file_list = []
			x = threading.Thread(target=whisper_function, args=(self,))
			x.start()

		def infer_sofa(self, ckpt, dictionary, op_format):
			self.prog_bar.set(0)
			self.prog_bar.start()

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

			self.prog_bar.stop()

		def run_sofa(self, ckpt, dictionary, op_format):
			x = threading.Thread(target=infer_sofa(self, ckpt, dictionary, op_format,))
			x.start()

		def startfile(self, filename):
			try:
				os.startfile(filename)
			except:
				subprocess.Popen(['xdg-open', filename])

		def change_disp_lang(self, choice):
			self.clang.set(choice)
			old_name_1 = self.tab_ttl_1
			old_name_2 = self.tab_ttl_2
			old_name_3 = self.tab_ttl_3
			self.cfg['disp_lang'] = choice
			with open('assets/cfg.yaml', 'w', encoding='utf-8') as f:
				yaml.dump(self.cfg, f, default_flow_style=False)
				f.close()
			# i hate this
			self.title(fxy(self._l[self.clang.get()]['app_ttl']))
			
			# renaming the tabs is a bit weird cuz doing it the normal way breaks everything lmao
			self.tabs._segmented_button._buttons_dict[old_name_1].configure(text=fxy(self._l[self.clang.get()]['tab_ttl_1']))
			self.tabs._segmented_button._buttons_dict[old_name_2].configure(text=fxy(self._l[self.clang.get()]['tab_ttl_2']))
			self.tabs._segmented_button._buttons_dict[old_name_3].configure(text=fxy(self._l[self.clang.get()]['tab_ttl_3']))

			self.corp_lbl.configure(text=fxy(self._l[self.clang.get()]['corpus_folder']))
			self.corp_btn.configure(text=fxy(self._l[self.clang.get()]['open']))
			self.what_lang.configure(text=fxy(self._l[self.clang.get()]['lang_choice']))
			self.trns_btn.configure(text=fxy(self._l[self.clang.get()]['run_trns']))
			self.model_lbl.configure(text=fxy(self._l[self.clang.get()]['model_lbl']))
			self.op_lbl.configure(text=fxy(self._l[self.clang.get()]['op_lbl']))
			self.align_btn.configure(text=fxy(self._l[self.clang.get()]['run_align']))
			self.set_lang_lbl.configure(text=fxy(self._l[self.clang.get()]['disp_lang']))
			self.set_wh_lbl.configure(text=fxy(self._l[self.clang.get()]['wh_model']))

		def update_wh_model(self):
			self.inf_wh_model.set(self.set_wh_cmbo.get())
			self.cfg['whisper_model'] = self.set_wh_cmbo.get()
			with open('assets/cfg.yaml', 'w', encoding='utf-8') as f:
				yaml.dump(self.cfg, f, default_flow_style=False)
				f.close()
			print(f"Set Whisper Model to {self.set_wh_cmbo.get()}")


		# non GUI config stuff
		# define and load strings
		self.cfg = {}
		with open('assets/cfg.yaml', 'r', encoding='utf-8') as c:
			try:
				self.cfg = yaml.safe_load(c)
			except yaml.YAMLError as exc:
				print(exc)
			c.close()

		# should this be a StringVar? :thonking:
		self.clang = ctk.StringVar(value=self.cfg['disp_lang'])
		self.inf_wh_model = ctk.StringVar(value=self.cfg['whisper_model'])

		self._l = {}
		with open('assets/lang.yaml', 'r', encoding='utf-8') as f:
			try:
				self._l = yaml.safe_load(f)
			except yaml.YAMLError as exc:
				print(exc)
			f.close()

		self.sofa_models = {}
		with open('assets/sofa_models.yaml', 'r', encoding='utf-8') as s:
			try:
				self.sofa_models = yaml.safe_load(s)
			except yaml.YAMLError as exc:
				print(exc)
			s.close()

		self.disp_lang = ctk.StringVar(value=self.clang.get())

		# window config
		self.title(fxy(self._l[self.clang.get()]['app_ttl']))
		self.geometry(f"{350}x{250}")
		self.resizable(height=False, width=False)

		# including this to prevent error when running on Linux
		if sys.platform == 'win32':
			self.wm_iconbitmap("assets/tgm.ico")

		# grid configs
		self.grid_columnconfigure(0, weight=1)
		self.grid_rowconfigure(0, weight=3)
		self.grid_rowconfigure(1, weight=0)

		# config tabs
		self.tabs = ctk.CTkTabview(self)
		self.tabs.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky=tk.NSEW)

		self.tab_ttl_1 = fxy(self._l[self.clang.get()]['tab_ttl_1'])
		self.tab_ttl_2 = fxy(self._l[self.clang.get()]['tab_ttl_2'])
		self.tab_ttl_3 = fxy(self._l[self.clang.get()]['tab_ttl_3'])

		self.tabs.add(self.tab_ttl_1)
		self.tabs.add(self.tab_ttl_2)
		self.tabs.add(self.tab_ttl_3)
		self.tabs.set(self.tab_ttl_1)

		# add copyright text :)
		self.credits = ctk.CTkLabel(self, text=fxy(self._l[self.clang.get()]['copyright']), text_color="gray50")
		self.credits.grid(row=1, column=1, padx=20, pady=5, sticky=tk.N)

		# progress bar
		self.prog_bar = ctk.CTkProgressBar(self,
										   orientation='horizontal',
										   mode='indeterminate')
		self.prog_bar.set(0)
		self.prog_bar.grid(row=1, column=0, padx=20, pady=5, sticky=tk.EW)

		#
		#	Whisper Tab GUI Codes
		#

		# whisper variables
		self.trans_lang_choice = ctk.StringVar(value='ENG') 

		# whisper tab grid configs
		self.tabs.tab(self.tab_ttl_1).grid_columnconfigure(0, weight=1)
		self.tabs.tab(self.tab_ttl_1).grid_columnconfigure(1, weight=1)
		self.tabs.tab(self.tab_ttl_1).grid_rowconfigure(0, weight=1)
		self.tabs.tab(self.tab_ttl_1).grid_rowconfigure(1, weight=1)

		# description label at the top
		self.corp_lbl = ctk.CTkLabel(self.tabs.tab(self.tab_ttl_1),
									 text=fxy(self._l[self.clang.get()]['corpus_folder']),
									 justify='left')
		self.corp_lbl.grid(row=0, column=0, padx=5, pady=5, sticky=tk.N)

		self.corp_btn = ctk.CTkButton(self.tabs.tab(self.tab_ttl_1),
									  text=fxy(self._l[self.clang.get()]['open']),
									  command=lambda: startfile(self, 'corpus'))
		self.corp_btn.grid(row=0, column=1, padx=5, pady=5, sticky=tk.N)

		# what lang are you transcribing?
		self.what_lang = ctk.CTkLabel(self.tabs.tab(self.tab_ttl_1),
									 text=fxy(self._l[self.clang.get()]['lang_choice']))
		self.what_lang.grid(row=1, column=0, padx=5, pady=5, sticky=tk.N)

		# lang combobox, just english for now :)
		self.transcribe_lang_op = ['EN', 'JP', 'ZH', 'ES', 'KO', 'RU', 'PT', 'FR', 'PL']
		self.lang_cmbo = ctk.CTkComboBox(self.tabs.tab(self.tab_ttl_1),
										 values=self.transcribe_lang_op,
										 command=cmbo_callback,
										 variable=self.trans_lang_choice)
		self.lang_cmbo.set('EN')
		self.lang_cmbo.grid(row=1, column=1, padx=5, pady=5, sticky=tk.N)

		# transcribe button
		self.trns_btn = ctk.CTkButton(self.tabs.tab(self.tab_ttl_1),
									  text=fxy(self._l[self.clang.get()]['run_trns']),
									  command=lambda: run_transcriber(self))
		self.trns_btn.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky=tk.NSEW)

		#
		#	Alignment Tab GUI Codes
		#

		# grid configs
		self.tabs.tab(self.tab_ttl_2).grid_columnconfigure((0, 1), weight=1)
		self.tabs.tab(self.tab_ttl_2).grid_rowconfigure((0, 1, 2), weight=3)

		self.model_choice = ctk.StringVar(value='tgm_sofa')
		self.op_mode = ctk.StringVar(value='htk')
		self.op_choices = ['TextGrid', 'htk']

		# choose sofa model
		self.model_lbl = ctk.CTkLabel(self.tabs.tab(self.tab_ttl_2),
									  text=fxy(self._l[self.clang.get()]['model_lbl']))
		self.model_lbl.grid(row=0, column=0, padx=5, pady=5, sticky=tk.N)

		# model choice combobox
		self.model_cmbo = ctk.CTkComboBox(self.tabs.tab(self.tab_ttl_2),
										  values=self.sofa_models['models'],
										  command=cmbo_callback,
										  variable=self.model_choice)
		self.model_cmbo.set(self.model_choice.get())
		self.model_cmbo.grid(row=0, column=1, padx=5, pady=5, sticky=tk.N)

		# choose format
		self.op_lbl = ctk.CTkLabel(self.tabs.tab(self.tab_ttl_2),
								   text=fxy(self._l[self.clang.get()]['op_lbl']))
		self.op_lbl.grid(row=1, column=0, padx=5, pady=5, sticky=tk.N)

		# model choice combobox
		self.op_cmbo = ctk.CTkComboBox(self.tabs.tab(self.tab_ttl_2),
									   values=self.op_choices,
									   command=cmbo_callback,
									   variable=self.op_mode)
		self.op_cmbo.set(self.op_mode.get())
		self.op_cmbo.grid(row=1, column=1, padx=5, pady=5, sticky=tk.N)

		# align button
		self.align_btn = ctk.CTkButton(self.tabs.tab(self.tab_ttl_2),
									   text=fxy(self._l[self.clang.get()]['run_align']),
									   command=lambda: run_sofa(self,
									   							self.sofa_models['models'][self.model_cmbo.get()]['ckpt_path'],
									   							self.sofa_models['models'][self.model_cmbo.get()]['dict_path'],
									   							self.op_cmbo.get()))
		self.align_btn.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky=tk.NSEW)

		#
		#	Settings Tab GUI Code
		#

		# grid configure
		self.tabs.tab(self.tab_ttl_3).grid_columnconfigure((0, 1), weight=1)
		self.tabs.tab(self.tab_ttl_3).grid_rowconfigure(0, weight=1)

		# choose display language
		self.set_lang_lbl = ctk.CTkLabel(self.tabs.tab(self.tab_ttl_3),
									     text=fxy(self._l[self.clang.get()]['disp_lang']))
		self.set_lang_lbl.grid(row=0, column=0, padx=5, pady=5, sticky=tk.N)

		# model choice combobox
		self.set_lang_cmbo = ctk.CTkComboBox(self.tabs.tab(self.tab_ttl_3),
										  	 values=self._l,
										  	 command=lambda x: change_disp_lang(self, self.clang.get()),
										  	 variable=self.clang)
		self.set_lang_cmbo.set(self.clang.get())
		self.set_lang_cmbo.grid(row=0, column=1, padx=5, pady=5, sticky=tk.N)

		self.set_wh_lbl = ctk.CTkLabel(self.tabs.tab(self.tab_ttl_3),
									   text=fxy(self._l[self.clang.get()]['wh_model']))
		self.set_wh_lbl.grid(row=1, column=0, padx=5, pady=5, sticky=tk.N)

		self.wh_models = ['tiny', 'base', 'small', 'medium', 'large']
		self.set_wh_cmbo = ctk.CTkComboBox(self.tabs.tab(self.tab_ttl_3),
										   values=self.wh_models,
										   command=lambda x: update_wh_model(self),
										   variable=self.inf_wh_model)
		self.set_wh_cmbo.grid(row=1, column=1, padx=5, pady=5, sticky=tk.N)



if __name__ == "__main__":
	app = App()
	app.mainloop()
