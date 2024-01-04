@ECHO off
cd /D %~dp0
call set_env.bat

echo SETUP WILL BEGIN

rem all the python setup is done here
python get-pip.py
python -m pip install torch==2.1.2+cu118 torchvision torchaudio -f https://download.pytorch.org/whl/cu118/torch_stable.html
python -m pip install -r SOFA/requirements.txt
python -m pip install openai-whisper customtkinter ftfy
python -m pip install gdown

echo INSTALLING MODELS + ASSETS

rem this installs the models + other big stuff, like ~800mb
python install_assets.py
move "colstone_sofa_v2.0.ckpt" "SOFA/ckpt"
move "tgm_sofa_v004.ckpt" "SOFA/ckpt"
del sofa_gui_asset_pack.zip

echo SETUP COMPLETE!!!
pause