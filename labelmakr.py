print('LabelMakr: A GUI Toolkit for SVS Label Generation. 2023 tigermeat (twitter@tigermeat_)\n')

# general stuff
import os, sys, re, glob
sys.path.append('.')

# GUI stuff
import customtkinter as ctk
import tkinter as tk
from ftfy import fix_text as fxy # unicode text all around fix
import threading
from pygame import mixer # for playing audio
from PIL import Image
from CTkListbox import *

# function stuff
import yaml
from pathlib import Path as p
import warnings

# LabelMakr specific functions
import sofa_func # basically just a script with sofa inference
import whisper_func # transcriber class is here
#import labbu_func # for label editing, coming in future update.

warnings.filterwarnings("ignore")

# default stuff configurations :)
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme(p('assets/ctk_tgm_theme.json'))
ctk.deactivate_automatic_dpi_awareness()

class transcriptEditor(ctk.CTkToplevel):
	def __init__(self, _l, clang, *args, **kwargs):
		super().__init__(*args, **kwargs)

		# save the language strings
		self._l = _l
		self.clang = clang

		self.main_window()

	def main_window(self):

		# configure window
		self.title(fxy(self._l[self.clang.get()]['transcription_editor']))
		self.geometry(f"{710}x{321}")
		self.resizable(height=True, width=True)
		self.minsize(width=710, height=321)
		if sys.platform == 'win32':
			if p('assets/tgm.icon').exists():
				self.wm_iconbitmap("assets/tgm.ico")
			self.after(200, lambda: self.iconbitmap(p('assets/tgm.ico')))

		self.grid_columnconfigure((0, 1), weight=1)
		self.grid_rowconfigure(0, weight=3)
		self.grid_rowconfigure(1, weight=1)

		#
		#	TEXT BOX
		#

		self.text_box = ctk.CTkTextbox(self, wrap='word', activate_scrollbars=True)
		self.text_box.grid(row=0, column=0, padx=(5, 0), pady=(5, 0), sticky=tk.NSEW)

		#
		#	FILE FRAME (Scrollable)
		#

		# file frame

		self.file_list = [file for file in glob.glob('corpus/**/*.txt')]

		# listbox
		self.file_sel = CTkListbox(self, width=155,
								   multiple_selection=False)
		self.file_sel.bind("<<ListboxSelect>>", lambda x: self.load_label())

		# placing all label files into the thingymajig.
		self.file_list_index = {}
		for i in range(len(self.file_list)):
			self.file_sel.insert(i, self.file_list[i])
			self.file_list_index[self.file_list[i]] = i
		
		self.file_sel.grid(row=0, column=1, rowspan=2, padx=5, pady=5, sticky=tk.NSEW)

		#
		#	BUTTON FRAME
		#

		self.button_frame = ctk.CTkFrame(self, height=50)
		self.button_frame.grid(row=1, column=0, padx=(5, 0), pady=5, sticky=tk.EW)

		self.button_frame.grid_rowconfigure(0, weight=0)

		# play button
		self.play_audio_btn = ctk.CTkButton(self.button_frame, 
											text=fxy(self._l[self.clang.get()]['play']), 
											width=90, command=lambda: self.play_audio())
		self.play_audio_btn.grid(row=0, column=0, padx=5, pady=5, sticky=tk.NS)

		# pause/unpause button
		self.pause_audio_btn = ctk.CTkButton(self.button_frame, 
											text=fxy(self._l[self.clang.get()]['pause']), 
											width=90, command=lambda: self.pause_audio())
		self.pause_audio_btn.grid(row=0, column=1, padx=5, pady=5, sticky=tk.NS)

		# stop button
		self.stop_audio_btn = ctk.CTkButton(self.button_frame, 
											text=fxy(self._l[self.clang.get()]['stop']),
											width=90, command=lambda: self.stop_audio())
		self.stop_audio_btn.grid(row=0, column=2, padx=5, pady=5, sticky=tk.NS)

		# save button
		self.save_lbl_btn = ctk.CTkButton(self.button_frame, 
										  text=fxy(self._l[self.clang.get()]['save']),
										  width=90, command=lambda: self.save_label())
		self.save_lbl_btn.grid(row=0, column=3, padx=5, pady=5, sticky=tk.NS)

		# save & next button
		self.save_next_btn = ctk.CTkButton(self.button_frame, 
										  text=fxy(self._l[self.clang.get()]['next']),
										  width=90, command=lambda: self.save_and_next())
		self.save_next_btn.grid(row=0, column=4, padx=5, pady=5, sticky=tk.NS)

	def load_label(self):

		self.text_box.delete("0.0", tk.END)

		open_path = p(self.file_sel.get(self.file_sel.curselection()))

		with open(open_path, 'r', encoding='utf-8') as lbl:
			self.text_box.insert("0.0", lbl.read())
			lbl.close()

	def save_label(self):

		save_path = p(self.file_sel.get(self.file_sel.curselection()))
		
		try:
			with open(save_path, 'w+', encoding='utf-8') as lbl:
				lbl.write(self.text_box.get("0.0", tk.END))
				lbl.close()
		except:
			print(f"Cannot write label for {self.file_sel.get(self.file_sel.curselection())}. ",
				  "Make sure you do not have it open in an external program.")

		print(f"Wrote label as {save_path}.")

	def save_and_next(self):
		# of course, save the label first
		self.save_label()
		index = self.file_sel.curselection()
		try:
			self.file_sel.activate(index+1)
			self.load_label()
		except:
			print('Cannot load next label!')

	def play_audio(self):
		try:
			mixer.init()
			sound_name = p(self.file_sel.get()).resolve()
			mixer.music.load(p(sound_name).with_suffix('.wav'))
			x = threading.Thread(target=mixer.music.play(), args=())
			x.start()
		except:
			print(f"Unable to play audio file {p(sound_name).with_suffix('.wav')}")

	def pause_audio(self):
		try:
			if mixer.music.get_busy():
				mixer.music.pause()
				self.pause_audio_btn.configure(text=fxy(self._l[self.clang.get()]['unpause']))
			else:
				mixer.music.unpause()
				self.pause_audio_btn.configure(text=fxy(self._l[self.clang.get()]['pause']))
		except:
			print('No audio to stop!')

	def stop_audio(self):
		try:
			mixer.music.stop()
			self.pause_audio_btn.configure(text=fxy(self._l[self.clang.get()]['pause']))
		except:
			print('Cannot stop music. Run for your life.')


class LabelMakr(ctk.CTk):
	def __init__(self):
		super().__init__()
		self.main_window()
		self.tr_editor = None
		
	def main_window(self):

		# non GUI config stuff
		# define and load strings
		self.cfg = {
			'disp_lang': 'en_US',
			'matmul': True,
			'whisper_model': 'medium'
		}
		if p('assets/cfg.yaml').exists():
			with open('assets/cfg.yaml', 'r', encoding='utf-8') as c:
				try:
					self.cfg.update(yaml.safe_load(c))
				except yaml.YAMLError as exc:
					print(exc)
				c.close()

		# should this be a StringVar? :thonking:
		self.clang = ctk.StringVar(value=self.cfg['disp_lang'])
		self.inf_wh_model = ctk.StringVar(value=self.cfg['whisper_model'])
		self.matmul_var = ctk.BooleanVar(value=self.cfg['matmul'])

		self._l = {}
		if p('assets/lang.yaml').exists():
			with open(p('assets/lang.yaml'), 'r', encoding='utf-8') as f:
				try:
					self._l = yaml.safe_load(f)
				except yaml.YAMLError as exc:
					print(exc)
				f.close()
		else:
			print('Cannot load language file in assets folder.')

		self.sofa_models = {}
		if p('assets/sofa_models.yaml').exists():
			with open('assets/sofa_models.yaml', 'r', encoding='utf-8') as s:
				try:
					self.sofa_models = yaml.safe_load(s)
				except yaml.YAMLError as exc:
					print(exc)
				s.close()
		else:
			print('Cannot load sofa model file in assets folder.')

		self.disp_lang = ctk.StringVar(value=self.clang.get())

		# window config
		self.title(fxy(self._l[self.clang.get()]['app_ttl']))
		self.geometry(f"{330}x{330}")
		self.resizable(height=False, width=True)
		self.minsize(width=330, height=330)

		# apparently trying to load an icon in linux breaks shit so. lawl.
		if sys.platform == 'win32':
			if p('assets/tgm.ico').exists():
				self.wm_iconbitmap(p('assets/tgm.ico'))
			else:
				print('Cannot load icon file.')

		#
		#	TITLE LABEL
		#

		self.grid_columnconfigure(0, weight=1)

		self.labelmakr_img = p('assets/labelmakr.png')
		self.labelmakr_logo = ctk.CTkImage(light_image=Image.open(self.labelmakr_img), size=(300,30))
		self.title_lbl = ctk.CTkLabel(self, image=self.labelmakr_logo, text='')
		self.title_lbl.grid(padx=5, pady=(10, 5), sticky=tk.EW)

		#
		#	Unnecessarily long tab configuration
		#

		# commented lines are for future features

		self.tabs = ctk.CTkTabview(self)
		self.tabs.grid(padx=5, pady=(0, 5), sticky=tk.EW)

		self.tab_ttl_1 = self.get_str('tab_ttl_1')
		self.tab_ttl_2 = self.get_str('tab_ttl_2')
		#self.tab_ttl_3 = self.get_str('tab_ttl_3')
		self.tab_ttl_4 = self.get_str('tab_ttl_4')

		self.tabs.add(self.tab_ttl_1)
		self.tabs.add(self.tab_ttl_2)
		#self.tabs.add(self.tab_ttl_3)
		self.tabs.add(self.tab_ttl_4)
		self.tabs.set(self.tab_ttl_1)

		# add copyright text :)
		self.credits = ctk.CTkLabel(self, text=fxy(self._l[self.clang.get()]['copyright']), text_color="gray50")
		self.credits.grid(padx=5, pady=(0, 5), sticky=tk.EW)

		#
		#	Whisper Tab GUI Codes
		#

		# whisper variables
		self.trans_lang_choice = ctk.StringVar(value='ENG') 

		# whisper tab grid configs
		self.tabs.tab(self.tab_ttl_1).grid_columnconfigure(0, weight=1)
		self.tabs.tab(self.tab_ttl_1).grid_columnconfigure(1, weight=1)
		self.tabs.tab(self.tab_ttl_1).grid_rowconfigure((0, 1), weight=1)
		self.tabs.tab(self.tab_ttl_1).grid_rowconfigure((2, 3), weight=3)

		# description label at the top
		self.corp_lbl = ctk.CTkLabel(self.tabs.tab(self.tab_ttl_1),
									 text=self.get_str('corpus_folder'),
									 justify='left')
		self.corp_lbl.grid(row=0, column=0, padx=5, pady=5, sticky=tk.N)

		self.corp_btn = ctk.CTkButton(self.tabs.tab(self.tab_ttl_1),
									  text=fxy(self._l[self.clang.get()]['open']),
									  command=lambda: self.startfolder('corpus'))
		self.corp_btn.grid(row=0, column=1, padx=5, pady=5, sticky=tk.N)

		# what lang are you transcribing?
		self.what_lang = ctk.CTkLabel(self.tabs.tab(self.tab_ttl_1),
									 text=fxy(self._l[self.clang.get()]['lang_choice']))
		self.what_lang.grid(row=1, column=0, padx=5, pady=5, sticky=tk.N)

		# lang combobox, just english for now :)
		self.transcribe_lang_op = ['EN', 'JP', 'ZH', 'FR']
		self.lang_cmbo = ctk.CTkComboBox(self.tabs.tab(self.tab_ttl_1),
										 values=self.transcribe_lang_op,
										 variable=self.trans_lang_choice)
		self.lang_cmbo.set('EN')
		self.lang_cmbo.grid(row=1, column=1, padx=5, pady=5, sticky=tk.N)

		# transcribe button
		self.trns_btn = ctk.CTkButton(self.tabs.tab(self.tab_ttl_1),
									  text=fxy(self._l[self.clang.get()]['run_trns']),
									  command=lambda: self.run_transcriber())
		self.trns_btn.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky=tk.NSEW)

		self.trns_edit = ctk.CTkButton(self.tabs.tab(self.tab_ttl_1),
									   text=fxy(self._l[self.clang.get()]['transcription_editor']),
									   command=lambda: self.open_transcription_editor())
		self.trns_edit.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky=tk.NSEW)

		#
		#	Alignment Tab GUI Codes
		#

		# grid configs
		self.tabs.tab(self.tab_ttl_2).grid_columnconfigure((0, 1), weight=1)
		self.tabs.tab(self.tab_ttl_2).grid_rowconfigure((0, 1), weight=1)
		self.tabs.tab(self.tab_ttl_2).grid_rowconfigure(2, weight=3)

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
									   variable=self.op_mode)
		self.op_cmbo.set(self.op_mode.get())
		self.op_cmbo.grid(row=1, column=1, padx=5, pady=5, sticky=tk.N)

		# align button
		self.align_btn = ctk.CTkButton(self.tabs.tab(self.tab_ttl_2),
									   text=fxy(self._l[self.clang.get()]['run_align']),
									   command=lambda: self.run_sofa(
									   							self.sofa_models['models'][self.model_cmbo.get()]['ckpt_path'],
									   							self.sofa_models['models'][self.model_cmbo.get()]['dict_path'],
									   							self.op_cmbo.get()))
		self.align_btn.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky=tk.NSEW)

		#
		#	Fix Label Tab GUI Code
		#

		#
		#	Settings Tab GUI Code
		#

		# grid configure
		self.tabs.tab(self.tab_ttl_4).grid_columnconfigure(0, weight=1)
		self.tabs.tab(self.tab_ttl_4).grid_columnconfigure(1, weight=3)
		self.tabs.tab(self.tab_ttl_4).grid_rowconfigure((0, 1, 2), weight=3)

		# choose display language
		self.set_lang_lbl = ctk.CTkLabel(self.tabs.tab(self.tab_ttl_4),
									     text=fxy(self._l[self.clang.get()]['disp_lang']))
		self.set_lang_lbl.grid(row=0, column=0, padx=5, pady=5, sticky=tk.N)

		# model choice combobox
		self.set_lang_cmbo = ctk.CTkComboBox(self.tabs.tab(self.tab_ttl_4),
										  	 values=self._l,
										  	 #command=lambda x: change_disp_lang(self, self.clang.get()),
										  	 command=lambda x: self.refresh(self.clang.get()),
										  	 variable=self.clang)
		self.set_lang_cmbo.set(self.clang.get())
		self.set_lang_cmbo.grid(row=0, column=1, padx=5, pady=5, sticky=tk.N)

		# choose whisper model label
		self.set_wh_lbl = ctk.CTkLabel(self.tabs.tab(self.tab_ttl_4),
									   text=fxy(self._l[self.clang.get()]['wh_model']))
		self.set_wh_lbl.grid(row=1, column=0, padx=5, pady=5, sticky=tk.N)

		# whisper label combobox
		self.wh_models = ['tiny', 'base', 'small', 'medium', 'large']
		self.set_wh_cmbo = ctk.CTkComboBox(self.tabs.tab(self.tab_ttl_4),
										   values=self.wh_models,
										   command=lambda x: update_wh_model(self),
										   variable=self.inf_wh_model)
		self.set_wh_cmbo.grid(row=1, column=1, padx=5, pady=5, sticky=tk.N)

		# tensorcore checkbox
		self.matmul_ckbx = ctk.CTkCheckBox(self.tabs.tab(self.tab_ttl_4),
										   variable=self.matmul_var,
										   onvalue=True,
										   offvalue=False,
										   text=fxy(self._l[self.clang.get()]['use_tensorcore']),
										   command=lambda: self.update_matmul())
		if self.cfg['matmul']:
			self.matmul_ckbx.select()
		elif not self.cfg['matmul']:
			self.matmul_ckbx.deselect()

		self.matmul_ckbx.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky=tk.N)

	def refresh(self, choice):
		# Better option for updating the display language tbh.
		self.cfg['disp_lang'] = choice
		with open('assets/cfg.yaml', 'w', encoding='utf-8') as f:
			yaml.dump(self.cfg, f, default_flow_style=False)
			f.close()
		self.destroy()
		app = LabelMakr()
		app.mainloop()

	def open_transcription_editor(self):
		if self.tr_editor is None or not self.tr_editor.winfo_exists():
			self.tr_editor = transcriptEditor(_l=self._l, clang=self.clang)
			self.tr_editor.after(10, self.tr_editor.lift)
		else:
			self.tr_editor.focus()

	def update_matmul(self):
		self.cfg['matmul'] = self.matmul_var.get()

		with open('assets/cfg.yaml', 'w', encoding='utf-8') as f:
			yaml.dump(self.cfg, f, default_flow_style=False)
			f.close()

		print(f"Updated matmul setting.")

	def run_transcriber(self):
		# initialize the whisper transcriber class
		print("Initializing Whisper")
		trnsr = whisper_func.Transcriber(self.trans_lang_choice.get(), self.inf_wh_model.get())
		# get a list of each file path needing transcription
		x = threading.Thread(target=whisper_func.Transcriber.run_transcription, args=(trnsr, self.trans_lang_choice.get(),))
		x.start()

	def run_sofa(self, ckpt, dictionary, op_format):
		x = threading.Thread(target=sofa_func.infer_sofa(ckpt, dictionary, op_format, self.matmul_var.get(), self.lang_cmbo.get(),))
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
			folder = p(foldername)
			#create the folder if it doesn't exist
			if(not folder.is_dir()):
				folder.mkdir()
			self.startfile(folder)

	def update_wh_model(self):
		self.inf_wh_model.set(self.set_wh_cmbo.get())
		self.cfg['whisper_model'] = self.set_wh_cmbo.get()
		with open('assets/cfg.yaml', 'w', encoding='utf-8') as f:
			yaml.dump(self.cfg, f, default_flow_style=False)
			f.close()
		print(f"Set Whisper Model to {self.set_wh_cmbo.get()}")

	def get_str(self, index):
		return fxy(self._l[self.clang.get()][index])

if __name__ == "__main__":
	app = LabelMakr()
	try:
		app.mainloop()
	except:
		print('Unable to open.')