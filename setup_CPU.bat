@ECHO off
cd /D %~dp0
call set_env.bat

echo Setting up python...
python get-pip.py
echo Setting up torch
python -m pip install torch torchvision torchaudio
python -m pip install -r assets/requirements.txt

rem model install
python install_assets.py

pause