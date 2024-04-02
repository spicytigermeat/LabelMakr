import labbu

class labbu_func:
	def __init__(self, lang=None):

		init_lang = lang
		if lang == 'EN':
			init_lang = 'default'
		if lang == 'FR':
			init_lang = 'millefeuille'
		if lang == 'JP':
			init_lang = 'japanese'

		self.labu = labbu.labbu(init_lang)
		self.dx_time = range(500, 500000)
		self.max_double_length = 150000
		self.max_super_short = 90000
		self.max_merge_len = 300000

	def load(self, lab_path):
		self.labu.load_lab(lab_path)

	def save(self, lab_path):
		self.labu.export_lab(lab_path)

	def get_phones(self, i):
		curr_pho = self.labu.curr_phone(i)
		next_pho = self.labu.next_phone(i)
		prev_pho = self.labu.prev_phone(i)
		return curr_pho, next_pho, prev_pho

	def dxer(self):
		for i in self.labu.labrange:
			cp, np, pp = self.get_phones(i)
			try:
				if self.labu.curr_phone(i) == 't' or self.labu.curr_phone(i) == 'd':
					if self.labu.is_type(pp, 'vowel') and self.labu.is_type(np, 'vowel') and self.labu.get_pho_len(i) in self.dx_time:
						#changes it to [dx]
						self.labu.change_phone(i, 'dx')
						try:
							i = i - 2
						except IndexError:
							pass
					if pp == 'r' and self.labu.is_type(np, 'vowel') and self.labu.get_pho_len(i) in dx_timing:
						self.labu.change_phone(i, 'dx')
						try:
							i = i - 2
						except IndexError:
							pass
			except:
				pass

	def fix_uh_r(self):
		for i in self.labu.labrange:
			cp, np, pp = self.get_phones(i)
			try:
				if cp == 'uh' and np == 'r':
					self.labu.merge(i, 'er')
					try:
						i = i - 2
					except IndexError:
						pass
			except:
				pass

	def merge_short_hh(self):
		for i in self.labu.labrange:
			cp, np, pp = self.get_phones(i)
			try:
				if np in ['hh', 'h'] and not self.labu.is_type(cp, 'vowel') and self.labu.get_pho_len(i+1) <= self.super_short:
					self.labu.merge(i, cp)
					try:
						i = i - 2
					except IndexError:
						pass
			except:
				pass

	def merge_dupes(self):
		for i in self.labu.labrange:
			cp, np, pp = self.get_phones(i)
			try:
				if cp == np:
					self.labu.merge(i, cp)
					try:
						i = i - 2
					except IndexError:
						pass
			except IndexError:
				pass