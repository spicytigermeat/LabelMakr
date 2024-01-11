@ECHO off
cd /D %~dp0
call set_env.bat
python labelmakr.py
pause