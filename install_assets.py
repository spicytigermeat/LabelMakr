import gdown
import zipfile

url = "1kQ2gSqAJsSsQB5KiATIJ4lRGPQp7_GvB"
output = "sofa_gui_asset_pack.zip"
gdown.download(id=url, output=output, quiet=False)

with zipfile.ZipFile('sofa_gui_asset_pack.zip', 'r') as archive:
	archive.extractall('.')