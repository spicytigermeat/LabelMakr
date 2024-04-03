import zipfile
import os
import requests
import logging
from pathlib import Path as P
from tqdm import tqdm

#
#	extract models into the proper location
#

# logger setup
logger = logging.getLogger(__name__)
logging.basicConfig(format="| %(levelname)s | %(message)s | %(asctime)s |",
					datefmt="%H:%M:%S")
logger.setLevel(logging.INFO)

logger.info('Downloading SOFA models.')

url = 'https://github.com/spicytigermeat/LabelMakr/releases/download/assets_v030/models.zip'
filepath = 'models.zip'
r = requests.get(url, stream=True)

total_size = int(r.headers.get('content-length', 0))
block_size = 1024

with tqdm(total=total_size, unit='B', unit_scale=True) as pbar:
	with open('models.zip', 'wb') as file:
		for data in r.iter_content(block_size):
			pbar.update(len(data))
			file.write(data)

if total_size != 0 and pbar.n != total_size:
	raise RuntimeError('Could not download file.')

logger.info('Sucessfully donwloaded models. Unzipping...')

with zipfile.ZipFile('models.zip', 'r') as archive:
	archive.extractall('./models')

os.remove('models.zip')

logger.info('Successfully downloaded models. You may exit this window.')