@ECHO off
cd /D %~dp0
call set_env.bat

echo Updating to v002!

rem sofa model v004
aria2c -d "SOFA/ckpt" https://github.com/spicytigermeat/SOFA-Models/releases/download/v0.0.4/tgm_sofa_v004.ckpt
aria2c -d "." https://raw.githubusercontent.com/spicytigermeat/SOFA_GUI/main/sofa_gui.py --continue="true" --allow-overwrite="true"
aria2c -d "assets" https://raw.githubusercontent.com/spicytigermeat/SOFA_GUI/main/assets/sofa_models.yaml --continue="true" --allow-overwrite="true"

echo Update is complete! You may close this window.
pause