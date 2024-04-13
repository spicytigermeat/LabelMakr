import os, sys, re
sys.path.append('.')
from glob import glob
import logging

# GUI stuff
import customtkinter as ctk
import tkinter as tk
from ftfy import fix_text as fxy # unicode text all around fix
import threading
from pygame import mixer # for playing audio
from PIL import Image
from CTkListbox import *
from CTkToolTip import *
from ezlocalizr import ezlocalizr
import pyglet

# function stuff
import yaml
from pathlib import Path as P

# LabelMakr specific functions
import sofa_func # basically just a script with sofa inference
import whisper_func # transcriber class is here
from labbu_func import labbu_func # for label editing, coming in future update.

#
#	default global config stuffs
#

pyglet.options['win32_gdi_font'] = True

DEBUG = True

ASSETS = P('./assets')
STRINGS = P('./strings')
CORPUS = P('./corpus')
MODELS = P('./models')

ctk.set_default_color_theme(P(ASSETS / 'ctk_tgm_theme.json'))
ctk.deactivate_automatic_dpi_awareness()

# logger setup
logger = logging.getLogger(__name__)
logging.basicConfig(format="| %(levelname)s | %(message)s | %(asctime)s |",
					datefmt="%H:%M:%S")
if DEBUG:
	logger.setLevel(logging.DEBUG)
logger.setLevel(logging.INFO)

assert ASSETS.exists(), logger.warning('Unable to locate assets folder.')
assert STRINGS.exists(), logger.warning('Unable to locate strings folder.')
assert CORPUS.exists(), os.mkdir(str(CORPUS))
assert MODELS.exists(), logger.warning('No SOFA models installed in \'models\' folder.')

def dummy():
	print('teehee :3c')

class LabelMakr(ctk.CTk):
	def __init__(self):
		super().__init__()
		
		# init global config
		self.cfg = {
			'disp_lang': 'en_US',
			'matmul': True,
			'whisper_model': 'medium',
			'dark_mode': True,
			'force_cpu': False
		}

		if P(ASSETS / 'cfg.yaml').exists():
			with open(P(ASSETS / 'cfg.yaml'), 'r', encoding='utf-8') as c:
				try:
					self.cfg.update(yaml.safe_load(c))
					c.close()
				except yaml.YAMLError as exc:
					logger.warning(f'Cannot load config file, using default dictionary.')

		# init variables from config
		self.clang = ctk.StringVar(value=self.cfg['disp_lang'])
		self.inf_wh_model = ctk.StringVar(value=self.cfg['whisper_model'])
		self.matmul_var = ctk.BooleanVar(value=self.cfg['matmul'])
		self.dark_mode = ctk.BooleanVar(value=self.cfg['dark_mode'])	
		self.force_cpu = ctk.BooleanVar(value=self.cfg['force_cpu'])

		# init SOFA models
		self.sofa_models = {'models':{}}
		for model in glob(str(MODELS / '*')):
			model = model[7:]
			# ignore the g2p model file
			if model in ['g2p_model.py', '__pycache__']:
				continue
			g2p_bool = False
			g2p_model = None
			g2p_cfg = None

			if P(MODELS / model / 'g2p').exists():
				g2p_bool = True
				g2p_model = P(MODELS / model / 'g2p/model.ptsd')
				g2p_cfg = P(MODELS / model / 'g2p/cfg.yaml')

			self.sofa_models['models'][model] = {
				'ckpt_path': P(MODELS / model / 'model.ckpt'),
				'dict_path': P(MODELS / model / 'dict.txt'),
				'g2p': g2p_bool,
				'g2p_model': g2p_model,
				'g2p_cfg': g2p_cfg
			}

		# init languages w/ezlocalizr
		self.L = ezlocalizr(language=self.clang.get(),
							string_path=STRINGS,
							default_lang='en_US')

		# init labbu for label fixes
		self.labu = labbu_func(lang='default')

		self.wh_models = ['tiny', 'base', 'small', 'medium', 'large']
		self.transcribe_lang_op = ['EN', 'JP', 'ZH', 'FR', 'KO']
		self.transcribe_lang_op.sort()

		# font stuff
		pyglet.font.add_file(str(P(ASSETS / 'PixelOperator.ttf')))
		pyglet.font.add_file(str(P(ASSETS / 'PixelMplus10-Regular.ttf')))
		pyglet.font.add_file(str(P(ASSETS / 'neodgm.ttf')))
		pyglet.font.add_file(str(P(ASSETS / 'WenQuanYi.Bitmap.Song.16px.ttf')))

		self.en_font = 'Pixel Operator'
		self.jp_font = 'PixelMPlus10'
		self.ko_font = 'NeoDunggeunmo'
		self.zh_font = 'WenQuanYi Bitmap Song 16px'

		if self.clang.get() in ['jp_JP']:
			self.font = ctk.CTkFont(family=self.jp_font, size=16)
			self.font_sm = ctk.CTkFont(family=self.jp_font, size=14)
		elif self.clang.get() in ['ko_KO']:
			self.font = ctk.CTkFont(family=self.ko_font, size=16)
			self.font_sm = ctk.CTkFont(family=self.ko_font, size=14)
		elif self.clang.get() in ['zh_ZH']:
			self.font = ctk.CTkFont(family=self.zh_font, size=18)
			self.font_sm = ctk.CTkFont(family=self.zh_font, size=16)
		else:
			self.font = ctk.CTkFont(family=self.en_font, size=16)
			self.font_sm = ctk.CTkFont(family=self.en_font, size=14)

		if self.dark_mode.get():
			ctk.set_appearance_mode("dark")
		else:
			ctk.set_appearance_mode("light")

		logger.info('Successfully initialized LabelMakr.')

		self.tr_editor = None
		self.main_window()
		
	def main_window(self):

		# window config
		self.title(self.L('app_ttl'))
		self.geometry(f"{420}x{380}")
		self.resizable(height=False, width=True)
		self.minsize(width=405, height=380)
		self.maxsize(width=600, height=380)
		self.tt_delay = 1

		# apparently trying to load an icon in linux breaks shit so. lawl.
		if sys.platform == 'win32':
			if P(ASSETS / 'tgm.ico').exists():
				self.wm_iconbitmap(P(ASSETS / 'tgm.ico'))

		#
		#	GUI Image Initialization
		#

		if P(ASSETS / 'labelmakr.png').exists():
			self.labelmakr_logo = ctk.CTkImage(light_image=Image.open(P(ASSETS / 'labelmakr.png')), size=(300,30))
		if P(ASSETS / 'folder.png').exists():
			self.folder_ico = ctk.CTkImage(light_image=Image.open(P(ASSETS / 'folder.png')))
		if P(ASSETS / 'trns.png').exists():
			self.trns_ico = ctk.CTkImage(light_image=Image.open(P(ASSETS / 'trns.png')))
		if P(ASSETS / 'trns_edit.png').exists():
			self.trns_edit_ico = ctk.CTkImage(light_image=Image.open(P(ASSETS / 'trns_edit.png')))
		if P(ASSETS / 'align.png').exists():
			self.align_ico = ctk.CTkImage(light_image=Image.open(P(ASSETS / 'align.png')))
		if P(ASSETS / 'fix.png').exists():	
			self.fix_ico = ctk.CTkImage(light_image=Image.open(P(ASSETS / 'fix.png')))

		#
		#	TITLE LABEL
		#

		self.grid_columnconfigure(0, weight=1)
		self.grid_columnconfigure(1, weight=1)
		self.grid_rowconfigure(0, weight=1)

		# logo at the top
		self.title_lbl = ctk.CTkLabel(self, image=self.labelmakr_logo, text='')
		self.title_lbl.grid(padx=5, pady=(10, 5), sticky=tk.EW, columnspan=2)

		# whisper variables
		self.trans_lang_choice = ctk.StringVar(value='EN') 

		# what lang are you transcribing?
		self.what_lang = ctk.CTkLabel(self,
									 text=self.L('lang_choice'),
									 font=self.font)
		self.what_lang.grid(row=1, column=0, padx=5, pady=(5, 0), sticky=tk.NE)

		self.lang_cmbo = ctk.CTkComboBox(self,
										 values=self.transcribe_lang_op,
										 variable=self.trans_lang_choice,
										 command=lambda x: self.change_transcription_language(),
										 font=self.font,
										 dropdown_font=self.font,
										 justify='center')
		self.lang_cmbo.set('EN')
		self.lang_cmbo.grid(row=1, column=1, padx=5, pady=5, sticky=tk.NW)
		self.lang_cmbo_tt = CTkToolTip(self.what_lang, delay=self.tt_delay, message=self.L('lang_choice_tt'), font=self.font)

		#
		#	Unnecessarily long tab configuration
		#

		# commented lines are for future features

		self.tabs = ctk.CTkTabview(self)
		self.tabs.grid(padx=5, pady=(0, 5), sticky=tk.EW, columnspan=2)

		self.tab_ttl_1 = self.L('tab_ttl_1')
		self.tab_ttl_2 = self.L('tab_ttl_2')
		self.tab_ttl_3 = self.L('tab_ttl_3')
		self.tab_ttl_4 = self.L('tab_ttl_4')

		self.tabs.add(self.tab_ttl_1)
		self.tabs.add(self.tab_ttl_2)
		self.tabs.add(self.tab_ttl_3)
		self.tabs.add(self.tab_ttl_4)
		self.tabs.set(self.tab_ttl_1)

		self.tabs._segmented_button.configure(font=self.font)

		# copyright label at the bottom of the screen
		self.credits = ctk.CTkLabel(self, 
									text=fxy('© tigermeat 2023-2024 | v030'), 
									text_color="gray50",
									font=self.font)
		self.credits.grid(padx=5, pady=(0, 5), sticky=tk.EW, columnspan=2)

		#
		#	Transcription Tab
		#

		self.tabs.tab(self.tab_ttl_1).grid_columnconfigure(0, weight=1)
		self.tabs.tab(self.tab_ttl_1).grid_columnconfigure(1, weight=1)
		self.tabs.tab(self.tab_ttl_1).grid_rowconfigure((0, 1, 2), weight=3)

		# open corpus button
		self.corp_btn = ctk.CTkButton(self.tabs.tab(self.tab_ttl_1),
									  text=self.L('corpus_folder'),
									  command=lambda: self.startfolder('corpus'),
									  image=self.folder_ico,
									  compound=tk.LEFT,
									  font=self.font)
		self.corp_btn.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky=tk.NSEW)
		self.corp_btn_tt = CTkToolTip(self.corp_btn, delay=self.tt_delay, message=self.L('corpus_folder_tt'), font=self.font)

		# transcribe button
		self.trns_btn = ctk.CTkButton(self.tabs.tab(self.tab_ttl_1),
									  text=self.L('run_trns'),
									  command=lambda: self.run_transcriber(),
									  image=self.trns_ico,
									  compound=tk.LEFT,
									  font=self.font)
		self.trns_btn.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky=tk.NSEW)
		self.trns_btn_tt = CTkToolTip(self.trns_btn, delay=self.tt_delay, message=self.L('run_trns_tt'), font=self.font)

		# transcription editor button
		self.trns_edit = ctk.CTkButton(self.tabs.tab(self.tab_ttl_1),
									   text=self.L('transcription_editor'),
									   command=lambda: self.open_transcription_editor(),
									   image=self.trns_edit_ico,
									   compound=tk.LEFT,
									   font=self.font)
		self.trns_edit.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky=tk.NSEW)
		self.trns_edit_tt = CTkToolTip(self.trns_edit, delay=self.tt_delay, message=self.L('transcription_editor_tt'), font=self.font)

		#
		#	Alignment Tab GUI Codes
		#

		# grid configs
		self.tabs.tab(self.tab_ttl_2).grid_columnconfigure((0, 1), weight=1)
		self.tabs.tab(self.tab_ttl_2).grid_rowconfigure((0, 1), weight=1)
		self.tabs.tab(self.tab_ttl_2).grid_rowconfigure(2, weight=3)

		self.model_choice = ctk.StringVar(value='tgm_sofa_en')
		self.op_mode = ctk.StringVar(value='htk')
		self.op_choices = ['htk', 'TextGrid']

		# choose sofa model
		self.model_lbl = ctk.CTkLabel(self.tabs.tab(self.tab_ttl_2),
									  text=self.L('model_lbl'),
									  font=self.font)
		self.model_lbl.grid(row=0, column=0, padx=5, pady=(10, 5), sticky=tk.N)
		self.model_lbl_tt = CTkToolTip(self.model_lbl, delay=self.tt_delay, message=self.L('model_lbl_tt'), font=self.font)

		# model choice combobox
		self.model_cmbo = ctk.CTkComboBox(self.tabs.tab(self.tab_ttl_2),
										  values=self.sofa_models['models'],
										  variable=self.model_choice,
										  font=self.font,
										  dropdown_font=self.font,
										  justify='center')
		self.model_cmbo.set(self.model_choice.get())
		self.model_cmbo.grid(row=1, column=0, padx=5, pady=5, sticky=tk.N)

		# choose format
		self.op_lbl = ctk.CTkLabel(self.tabs.tab(self.tab_ttl_2),
								   text=self.L('op_lbl'),
								   font=self.font)
		self.op_lbl.grid(row=0, column=1, padx=5, pady=(10, 5), sticky=tk.N)
		self.op_lbl_tt = CTkToolTip(self.op_lbl, delay=self.tt_delay, message=self.L('op_lbl_tt'), font=self.font)

		# model choice combobox
		self.op_cmbo = ctk.CTkComboBox(self.tabs.tab(self.tab_ttl_2),
									   values=self.op_choices,
									   variable=self.op_mode,
									   font=self.font,
									   dropdown_font=self.font,
									   justify='center')
		self.op_cmbo.set(self.op_mode.get())
		self.op_cmbo.grid(row=1, column=1, padx=5, pady=5, sticky=tk.N)

		# align button
		self.align_btn = ctk.CTkButton(self.tabs.tab(self.tab_ttl_2),
									   text=self.L('run_align'),
									   command=lambda: self.run_sofa(
				   							self.sofa_models['models'][self.model_cmbo.get()]['ckpt_path'],
				   							self.sofa_models['models'][self.model_cmbo.get()]['dict_path'],
				   							self.sofa_models['models'][self.model_cmbo.get()]['g2p'],
				   							self.sofa_models['models'][self.model_cmbo.get()]['g2p_model'],
				   							self.sofa_models['models'][self.model_cmbo.get()]['g2p_cfg']),
									   image=self.align_ico,
									   compound=tk.LEFT,
									   font=self.font)
		self.align_btn.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky=tk.NSEW)
		self.align_btn_tt = CTkToolTip(self.align_btn, delay=self.tt_delay, message=self.L('run_align_tt'), font=self.font)

		#
		#	Fix Label Tab GUI Code
		#

		self.tabs.tab(self.tab_ttl_3).grid_columnconfigure((0, 1), weight=1)
		self.tabs.tab(self.tab_ttl_3).grid_rowconfigure(0, weight=0)
		self.tabs.tab(self.tab_ttl_3).grid_rowconfigure((1, 2), weight=1)
		self.tabs.tab(self.tab_ttl_3).grid_rowconfigure(3, weight=3)

		# help label
		self.labbu_help = ctk.CTkLabel(self.tabs.tab(self.tab_ttl_3),
									   text=self.L('labbu_help'),
									   font=self.font_sm,
									   text_color='lightgray',)
		self.labbu_help.grid(row=0, column=0, columnspan=2, padx=5, pady=2.5, sticky=tk.NSEW)

		# dxer box
		self.dxer = ctk.BooleanVar(value=True)
		self.dxer_cb = ctk.CTkCheckBox(self.tabs.tab(self.tab_ttl_3),
									   variable=self.dxer,
									   onvalue=True,
									   offvalue=False,
									   text=self.L('dxer'),
									   font=self.font)
		self.dxer_cb.grid(row=1, column=0, padx=5, pady=5, sticky=tk.N)
		self.dxer_cb_tt = CTkToolTip(self.dxer_cb, delay=self.tt_delay, message=self.L('dxer_tt'), font=self.font)

		# uhr merge
		self.uhr_merge = ctk.BooleanVar(value=True)
		self.uhr_merge_cb = ctk.CTkCheckBox(self.tabs.tab(self.tab_ttl_3),
											variable=self.uhr_merge,
											onvalue=True,
											offvalue=False,
											text=self.L('uhr_merge'),
											font=self.font)
		self.uhr_merge_cb.grid(row=1, column=1, padx=5, pady=5, sticky=tk.N)
		self.uhr_merge_tt = CTkToolTip(self.uhr_merge_cb, delay=self.tt_delay, message=self.L('uhr_merge_tt'), font=self.font)

		# merge duplicates
		self.merge_dupes = ctk.BooleanVar(value=True)
		self.merge_dupes_cb = ctk.CTkCheckBox(self.tabs.tab(self.tab_ttl_3),
											  variable=self.merge_dupes,
											  onvalue=True,
											  offvalue=False,
											  text=self.L('merge_dupes'),
											  font=self.font)
		self.merge_dupes_cb.grid(row=2, column=0, padx=5, pady=5, sticky=tk.N)
		self.merge_dupes_tt = CTkToolTip(self.merge_dupes_cb, delay=self.tt_delay, message=self.L('merge_dupes_tt'), font=self.font)

		# merge h
		self.merge_h = ctk.BooleanVar(value=True)
		self.merge_h_cb = ctk.CTkCheckBox(self.tabs.tab(self.tab_ttl_3),
										  variable=self.merge_h,
										  onvalue=True,
										  offvalue=False,
										  text=self.L('short_h'),
										  font=self.font)
		self.merge_h_cb.grid(row=2, column=1, padx=5, pady=5, sticky=tk.N)
		self.merge_h_tt = CTkToolTip(self.merge_h_cb, delay=self.tt_delay, message=self.L('short_h_tt'), font=self.font)

		# run fix button
		self.run_fix_btn = ctk.CTkButton(self.tabs.tab(self.tab_ttl_3),
									     text=self.L('run_fix'),
									     command=lambda: self.run_label_fix(),
									     image=self.fix_ico,
									     compound=tk.LEFT,
									     font=self.font)
		self.run_fix_btn.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky=tk.NSEW)
		self.run_fix_tt = CTkToolTip(self.run_fix_btn, delay=self.tt_delay, message=self.L('run_fix_tt'), font=self.font)

		#
		#	Settings Tab GUI Code
		#

		# grid configure
		self.tabs.tab(self.tab_ttl_4).grid_columnconfigure((0, 1), weight=1)
		self.tabs.tab(self.tab_ttl_4).grid_rowconfigure((0, 1, 2, 3), weight=1)

		# choose display language
		self.set_lang_lbl = ctk.CTkLabel(self.tabs.tab(self.tab_ttl_4),
									     text=self.L('disp_lang'),
									     font=self.font)
		self.set_lang_lbl.grid(row=0, column=0, padx=5, pady=5, sticky=tk.N)
		self.set_lang_lbl_tt = CTkToolTip(self.set_lang_lbl, delay=self.tt_delay, message=self.L('disp_lang_tt'), font=self.font)

		# model choice combobox
		self.set_lang_cmbo = ctk.CTkComboBox(self.tabs.tab(self.tab_ttl_4),
										  	 values=self.L.lang_list,
										  	 command=lambda x: self.refresh(self.clang.get()),
										  	 variable=self.clang,
										  	 font=self.font,
										  	 dropdown_font=self.font,
										  	 justify='center')
		self.set_lang_cmbo.set(self.clang.get())
		self.set_lang_cmbo.grid(row=1, column=0, padx=5, pady=5, sticky=tk.N)

		# choose whisper model label
		self.set_wh_lbl = ctk.CTkLabel(self.tabs.tab(self.tab_ttl_4),
									   text=self.L('wh_model'),
									   font=self.font)
		self.set_wh_lbl.grid(row=0, column=1, padx=5, pady=5, sticky=tk.N)
		self.set_wh_lbl_tt = CTkToolTip(self.set_wh_lbl, delay=self.tt_delay, message=self.L('wh_model_tt'), font=self.font)

		# whisper label combobox
		self.set_wh_cmbo = ctk.CTkComboBox(self.tabs.tab(self.tab_ttl_4),
										   values=self.wh_models,
										   command=lambda x: self.update_wh_model(),
										   variable=self.inf_wh_model,
										   font=self.font,
										   dropdown_font=self.font,
										   justify='center')
		self.set_wh_cmbo.grid(row=1, column=1, padx=5, pady=5, sticky=tk.N)

		# tensorcore checkbox
		self.matmul_ckbx = ctk.CTkCheckBox(self.tabs.tab(self.tab_ttl_4),
										   variable=self.matmul_var,
										   onvalue=True,
										   offvalue=False,
										   text=self.L('use_tensorcore'),
										   command=lambda: self.update_matmul(),
										   font=self.font)
		if self.cfg['matmul']:
			self.matmul_ckbx.select()
		elif not self.cfg['matmul']:
			self.matmul_ckbx.deselect()

		self.matmul_ckbx.grid(row=2, column=0, padx=5, pady=5, sticky=tk.N)
		self.matmul_ckbx_tt = CTkToolTip(self.matmul_ckbx, delay=self.tt_delay, message=self.L('use_tensorcore_tt'), font=self.font)

		# force CPU rendering checkbox
		self.force_cpu_ckbx = ctk.CTkCheckBox(self.tabs.tab(self.tab_ttl_4),
											  variable=self.force_cpu,
											  onvalue=True,
											  offvalue=False,
											  text=self.L('force_cpu'),
											  command=lambda: self.update_cpu_render(),
											  font=self.font)
		self.force_cpu_ckbx.grid(row=2, column=1, padx=5, pady=5, sticky=tk.N)
		self.force_cpu_ckbx_tt = CTkToolTip(self.force_cpu_ckbx, delay=self.tt_delay, message=self.L('force_cpu_tt'), font=self.font)

		# appearance checkbox
		self.appearance_rbtn = ctk.CTkCheckBox(self.tabs.tab(self.tab_ttl_4),
											   variable=self.dark_mode,
											   onvalue=True,
											   offvalue=False,
											   text=self.L('dark_mode'),
											   command=lambda: self.change_appearance(),
											   font=self.font)
		self.appearance_rbtn.grid(row=3, column=0, padx=5, pady=5, sticky=tk.N)
		self.appearance_rbtn_tt = CTkToolTip(self.appearance_rbtn, delay=self.tt_delay, message=self.L('dark_mode_tt'), font=self.font)

	def refresh(self, choice):
		# Better option for updating the display language tbh.
		self.cfg['disp_lang'] = choice
		with open(P(ASSETS / 'cfg.yaml'), 'w', encoding='utf-8') as f:
			yaml.dump(self.cfg, f, default_flow_style=False)
			f.close()
		self.L.load_lang(choice)

		logger.info(f'Set display language to {choice}')

		self.destroy()
		app = LabelMakr()
		app.mainloop()

	def open_transcription_editor(self):
		if self.tr_editor is None or not self.tr_editor.winfo_exists():
			self.tr_editor = transcriptEditor(L=self.L, clang=self.clang, font=self.font)
			self.tr_editor.after(10, self.tr_editor.lift)
		else:
			self.tr_editor.focus()

	def update_matmul(self):
		self.cfg['matmul'] = self.matmul_var.get()

		with open(P(ASSETS / 'cfg.yaml'), 'w', encoding='utf-8') as f:
			yaml.dump(self.cfg, f, default_flow_style=False)
			f.close()

		logger.info(f'Updated matmul setting')

	def run_transcriber(self):
		# initialize the whisper transcriber class
		logger.info('Initializing Whisper')

		# forces small Whisper model upon using "CPU" only mode so your PC don't explode
		inference_model = self.inf_wh_model.get()
		if self.force_cpu.get():
			inference_model = 'small'

		trnsr = whisper_func.Transcriber(self.trans_lang_choice.get(), inference_model)

		x = threading.Thread(target=whisper_func.Transcriber.run_transcription, args=(trnsr, self.trans_lang_choice.get(),))
		x.start()

	def run_sofa(self,
				 ckpt: str,
				 dictionary: str,
				 g2p_bool: bool,
				 g2p_model: str,
				 g2p_cfg: str
		):
		x = threading.Thread(target=sofa_func.infer_sofa(ckpt, dictionary, self.op_cmbo.get(), self.matmul_var.get(), self.lang_cmbo.get(), g2p_bool, g2p_model, g2p_cfg,))
		x.start()

	def startfile(self, filename):
		try:
			os.startfile(filename)
		except:
			subprocess.Popen(['xdg-open', filename])

	def startfolder(self, foldername):
			"""
			Open a folder in file explorer
			If the folder doesn't exist, create it.
			"""
			folder = P(foldername)
			#create the folder if it doesn't exist
			if(not folder.is_dir()):
				folder.mkdir()
			self.startfile(folder)

	def update_wh_model(self):
		self.inf_wh_model.set(self.set_wh_cmbo.get())
		self.cfg['whisper_model'] = self.set_wh_cmbo.get()
		with open(P(ASSETS / 'cfg.yaml'), 'w', encoding='utf-8') as f:
			yaml.dump(self.cfg, f, default_flow_style=False)
			f.close()
		logger.info(f"Set Whisper Model to {self.set_wh_cmbo.get()}")

	def update_cpu_render(self):
		'''
		wip
		'''
		return 0

	def run_label_fix(self):
		# uses labbu to fix the files

		corpus_list = [name for name in os.listdir(str(P(CORPUS))) if os.path.isdir(str(P(CORPUS / name)))]

		for singer in corpus_list:
			for file in glob(str(P(f'./corpus/{singer}/labels/*.lab')), recursive=True):
				self.labu.load(file)

				if self.dxer_cb.get():
					self.labu.dxer()
				if self.uhr_merge_cb.get():
					self.labu.fix_uh_r()
				if self.merge_h_cb.get():
					self.labu.merge_short_hh()
				if self.merge_dupes_cb.get():
					self.labu.merge_dupes()

				self.labu.save(file)
		logger.info('Finished fixing labels!')

	def change_transcription_language(self):
		if self.lang_cmbo.get() == 'EN':
			self.dxer_cb.select()
			self.dxer_cb.configure(state="normal")
			self.uhr_merge_cb.select()
			self.uhr_merge_cb.configure(state="normal")
		else:
			self.dxer_cb.deselect()
			self.dxer_cb.configure(state="disabled")
			self.uhr_merge_cb.deselect()
			self.uhr_merge_cb.configure(state="disabled")

	def change_appearance(self):
		self.dark_mode = self.appearance_rbtn.get()

		self.cfg['dark_mode'] = self.dark_mode

		with open(P(ASSETS / 'cfg.yaml'), 'w', encoding='utf-8') as f:
			yaml.dump(self.cfg, f, default_flow_style=False)
			f.close()

		if self.dark_mode:
			ctk.set_appearance_mode('dark')
			logger.info('Toggled dark mode.')
		else:
			ctk.set_appearance_mode('light')
			logger.info('Toggled light mode.')

class transcriptEditor(ctk.CTkToplevel):
	def __init__(self, L, clang, font):
		super().__init__()
		# carry over needed things from the main class
		self.L = L
		self.clang = clang
		self.font = font
		self.tt_delay = 1

		# custom mixer wrapper cuz the pause function is weird
		self.player = mixer_wrapper()

		self.main_window()

	def main_window(self):

		# configure window
		self.title(self.L('transcription_editor'))
		self.geometry(f"{710}x{361}")
		self.resizable(height=True, width=True)
		self.minsize(width=710, height=361)

		if sys.platform == 'win32':
			if P(ASSETS / 'tgm.icon').exists():
				self.wm_iconbitmap(ASSETS / 'tgm.ico')
			self.after(200, lambda: self.iconbitmap(P('assets/tgm.ico')))

		self.grid_columnconfigure((0, 1), weight=1)
		self.grid_rowconfigure(0, weight=0)
		self.grid_rowconfigure((1, 2), weight=1)

		#
		#	Image variable initilization
		#

		if P(ASSETS / 'labelmakr.png').exists():
			self.labelmakr_logo = ctk.CTkImage(light_image=Image.open(P(ASSETS / 'labelmakr.png')), size=(300,30))
		if P(ASSETS / 'play.png').exists():
			self.play_ico = ctk.CTkImage(light_image=Image.open(P(ASSETS / 'play.png')))
		if P(ASSETS / 'pause.png').exists():
			self.pause_ico = ctk.CTkImage(light_image=Image.open(P(ASSETS / 'pause.png')))
		if P(ASSETS / 'stop.png').exists():
			self.stop_ico = ctk.CTkImage(light_image=Image.open(P(ASSETS / 'stop.png')))
		if P(ASSETS / 'save.png').exists():
			self.save_ico = ctk.CTkImage(light_image=Image.open(P(ASSETS / 'save.png')))
		if P(ASSETS / 'fastfw.png').exists():
			self.next_ico = ctk.CTkImage(light_image=Image.open(P(ASSETS / 'fastfw.png')))

		#
		#	Image at the top
		#

		# logo at the top
		self.title_lbl = ctk.CTkLabel(self, image=self.labelmakr_logo, text='')
		self.title_lbl.grid(padx=(10, 0), pady=(10, 5), sticky=tk.NW, columnspan=2)

		#
		#	TEXT BOX
		#

		self.text_box = ctk.CTkTextbox(self, 
									   wrap='word',
									   activate_scrollbars=True,
									   font=self.font)
		self.text_box.grid(row=1, column=0, padx=(5, 0), pady=(5, 0), sticky=tk.NSEW)

		#
		#	FILE FRAME (Scrollable)
		#

		# file frame

		self.file_list = [file[7:] for file in glob(str(P(CORPUS / '**/*.txt')))]

		# listbox
		self.file_sel = CTkListbox(self, width=155,
								   multiple_selection=False,
								   font=self.font)
		self.file_sel.bind("<<ListboxSelect>>", lambda x: self.load_label())

		# placing all label files into the thingymajig.
		self.file_list_index = {}
		for i, file in enumerate(self.file_list):
			self.file_sel.insert(i, file)
			self.file_list_index[file] = i
		
		self.file_sel.grid(row=1, column=1, rowspan=2, padx=5, pady=5, sticky=tk.NSEW)

		#
		#	BUTTON FRAME
		#

		self.button_frame = ctk.CTkFrame(self, height=50)
		self.button_frame.grid(row=2, column=0, padx=(5, 0), pady=5, sticky=tk.NSEW)

		self.button_frame.grid_rowconfigure(0, weight=3)

		# play button
		self.play_audio_btn = ctk.CTkButton(self.button_frame, 
											image=self.play_ico,
											text='',
											width=91,
											command=lambda: self.play_audio())
		self.play_audio_btn.grid(row=0, column=0, padx=5, pady=5, sticky=tk.NSEW)
		self.play_audio_btn_tt = CTkToolTip(self.play_audio_btn, delay=self.tt_delay, message=self.L('play'), font=self.font)

		# pause/unpause button
		self.pause_audio_btn = ctk.CTkButton(self.button_frame, 
											image=self.pause_ico,
											text='', 
											width=91, 
											command=lambda: self.pause_audio())
		self.pause_audio_btn.grid(row=0, column=1, padx=5, pady=5, sticky=tk.NSEW)
		self.pause_audio_btn_tt = CTkToolTip(self.pause_audio_btn, delay=self.tt_delay, message=self.L('pause'), font=self.font)

		# stop button
		self.stop_audio_btn = ctk.CTkButton(self.button_frame, 
											image=self.stop_ico,
											text='',
											width=91,
											command=lambda: self.stop_audio())
		self.stop_audio_btn.grid(row=0, column=2, padx=5, pady=5, sticky=tk.NSEW)
		self.stop_audio_btn_tt = CTkToolTip(self.stop_audio_btn, delay=self.tt_delay, message=self.L('stop'), font=self.font)

		# save button
		self.save_lbl_btn = ctk.CTkButton(self.button_frame,
										  image=self.save_ico,
										  text='',
										  width=91,
										  command=lambda: self.save_label())
		self.save_lbl_btn.grid(row=0, column=3, padx=5, pady=5, sticky=tk.NSEW)
		self.save_lbl_btn_tt = CTkToolTip(self.save_lbl_btn, delay=self.tt_delay, message=self.L('save'), font=self.font)

		# save & next button
		self.save_next_btn = ctk.CTkButton(self.button_frame, 
										  image=self.next_ico,
										  text='',
										  width=91,
										  command=lambda: self.save_and_next())
		self.save_next_btn.grid(row=0, column=4, padx=5, pady=5, sticky=tk.NSEW)
		self.save_next_btn_tt = CTkToolTip(self.save_next_btn, delay=self.tt_delay, message=self.L('next'), font=self.font)

	def load_label(self):

		self.text_box.delete("0.0", tk.END)

		# load audio
		sound_name = CORPUS / P(self.file_sel.get()).resolve()

		self.player.load(P(sound_name).with_suffix('.wav'))

		open_path = CORPUS / P(self.file_sel.get(self.file_sel.curselection()))

		with open(open_path, 'r', encoding='utf-8') as lbl:
			self.text_box.insert("0.0", lbl.read())
			lbl.close()

	def save_label(self):

		save_path = P(CORPUS / self.file_sel.get(self.file_sel.curselection()))
		
		try:
			with open(save_path, 'w+', encoding='utf-8') as lbl:
				lbl.write(self.text_box.get("0.0", tk.END))
				lbl.close()
		except:
			logger.warning(f"Cannot write label for {self.file_sel.get(self.file_sel.curselection())}. ",
				  "Make sure you do not have it open in an external program.")

		logger.info(f'Wrote label as {str(save_path)}')

	def save_and_next(self):
		# of course, save the label first
		self.save_label()
		index = self.file_sel.curselection()
		try:
			self.file_sel.activate(index+1)
			self.load_label()
		except:
			logger.warning('Cannot load next label')

	def play_audio(self):
		try:
			x = threading.Thread(target=self.player.play(), args=())
			x.start()
		except:
			logger.warning(f"Unable to play audio file {P(sound_name).with_suffix('.wav')}")

	def pause_audio(self):
		try:
			if self.player.busy:
				self.pause_audio_btn.configure(image=self.play_ico)
			else:
				self.pause_audio_btn.configure(image=self.pause_ico)
			self.player.pause()
		except:
			logger.info('No audio to stop.')

	def stop_audio(self):
		try:
			self.player.stop()
			self.pause_audio_btn.configure(image=self.pause_ico)
		except:
			logger.warning('Cannot stop music. Run for your life.')

class mixer_wrapper:
	def __init__(self):
		'''
		Silly class for forcing pygame mixer to work better lol
		'''
		self.is_paused = False
		self.hit_play = False
		mixer.init()

	def load(self, audio):
		mixer.music.load(audio)
		self.hit_play = False

	def play(self):
		mixer.music.play()
		self.hit_play = True

	def pause(self):
		if self.hit_play:
			if self.is_paused:
				mixer.music.unpause()
				self.is_paused = False
			elif not self.is_paused:
				mixer.music.pause()
				self.is_paused = True

	def stop(self):
		mixer.music.stop()
		self.hit_play = False

	@property
	def busy(self) -> bool:
		return mixer.music.get_busy()

def main():
	app = LabelMakr()
	app.mainloop()

if __name__ == "__main__":
	main()