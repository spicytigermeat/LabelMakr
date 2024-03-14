import gdown
import zipfile
with zipfile.ZipFile('labelmakr_assets.zip', 'r') as archive:
	archive.extractall('.')
