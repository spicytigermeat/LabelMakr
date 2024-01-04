@ECHO off
cd /D %~dp0
call set_env.bat
python sofa_gui.py
pause