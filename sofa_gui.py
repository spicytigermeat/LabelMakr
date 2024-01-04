# general stuff
import os, sys, re, glob
sys.path.append('.')
# GUI stuff
import customtkinter as ctk
import tkinter as tk
from ftfy import fix_text as fxy # unicode text all around fix
import threading
# function stuff
import yaml
import pathlib
import warnings

import sofa_func # basically just a script with sofa inference
import whisper_func # transcriber class is here

warnings.filterwarnings("ignore")

# default stuff configurations :)
ctk.set_appearance_mode("System")
ctk.set_default_color_theme('assets/ctk_tgm_theme.json')
ctk.deactivate_automatic_dpi_awareness()

class App(ctk.CTk):
	def __init__(self):
		super().__init__()
		self.main_window()
		
	def main_window(self):

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

		# apparently trying to load an icon in linux breaks shit so. lawl.
		if sys.platform == 'win32':
			self.wm_iconbitmap("assets/tgm.ico")

		def cmbo_callback(choice):
			print('selected option:', choice)

		def run_transcriber(self):
			# initialize the whisper transcriber class
			print("Initializing Whisper")
			trnsr = whisper_func.Transcriber(self.trans_lang_choice.get(), self.inf_wh_model.get())
			# get a list of each file path needing transcription
			x = threading.Thread(target=whisper_func.Transcriber.run_transcription, args=(trnsr, self.trans_lang_choice.get(),))
			x.start()

		def run_sofa(self, ckpt, dictionary, op_format):
			x = threading.Thread(target=sofa_func.infer_sofa(ckpt, dictionary, op_format,))
			x.start()

		def startfile(self, filename):
			try:
				os.startfile(filename)
			except:
				subprocess.Popen(['xdg-open', filename])

		def update_wh_model(self):
			self.inf_wh_model.set(self.set_wh_cmbo.get())
			self.cfg['whisper_model'] = self.set_wh_cmbo.get()
			with open('assets/cfg.yaml', 'w', encoding='utf-8') as f:
				yaml.dump(self.cfg, f, default_flow_style=False)
				f.close()
			print(f"Set Whisper Model to {self.set_wh_cmbo.get()}")

		def get_str(self, index):
			return fxy(self._l[self.clang.get()][index])

		# grid configs
		self.grid_columnconfigure(0, weight=1)
		self.grid_rowconfigure(0, weight=3)
		self.grid_rowconfigure(1, weight=0)

		# config tabs
		self.tabs = ctk.CTkTabview(self)
		self.tabs.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky=tk.NSEW)

		self.tab_ttl_1 = get_str(self, 'tab_ttl_1')
		self.tab_ttl_2 = get_str(self, 'tab_ttl_2')
		self.tab_ttl_3 = get_str(self, 'tab_ttl_3')

		self.tabs.add(self.tab_ttl_1)
		self.tabs.add(self.tab_ttl_2)
		self.tabs.add(self.tab_ttl_3)
		self.tabs.set(self.tab_ttl_1)

		# add copyright text :)
		self.credits = ctk.CTkLabel(self, text=fxy(self._l[self.clang.get()]['copyright']), text_color="gray50")
		self.credits.grid(row=1, column=1, padx=20, pady=5, sticky=tk.N)

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
									 text=get_str(self, 'corpus_folder'),
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
										  	 #command=lambda x: change_disp_lang(self, self.clang.get()),
										  	 command=lambda x: self.refresh(self.clang.get()),
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

	def refresh(self, choice):
		# Better option for updating the display language tbh.
		self.cfg['disp_lang'] = choice
		with open('assets/cfg.yaml', 'w', encoding='utf-8') as f:
			yaml.dump(self.cfg, f, default_flow_style=False)
			f.close()
		self.destroy()
		app = App()
		app.mainloop()

if __name__ == "__main__":
	app = App()
	try:
		app.mainloop()
	except:
		print('Unable to open.')