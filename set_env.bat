rem reference from https://hituji-ws.com/code/python/python-emb-usage/
SET DP0=%~dp0
SET DP0=%DP0:~0,-1%

rem overriding windows user/local environment
SET LOCALENV_DIR=%DP0%\_local_env
SET TMP=%LOCALENV_DIR%\_tmp
SET TEMP=%LOCALENV_DIR%\_tmp
SET HOME=%LOCALENV_DIR%\userprofile
SET HOMEPATH=%LOCALENV_DIR%\userprofile
SET LOCALAPPDATA=%LOCALENV_DIR%\localappdata
SET APPDATA=%LOCALENV_DIR%\userroaming

SET PYTHON_PATH=%DP0%\python

rem overriding default python env vars in order to interfere with any system python installation
SET PYTHONHOME=
SET PYTHONPATH=
SET PYTHONEXECUTABLE=%PYTHON_PATH%\python.exe
SET PYTHONWEXECUTABLE=%PYTHON_PATH%\pythonw.exe

SET PYTHON_EXECUTABLE=%PYTHON_PATH%\python.exe
SET PYTHONW_EXECUTABLE=%PYTHON_PATH%\pythonw.exe
SET PYTHON_BIN_PATH=%PYTHON_EXECUTABLE%
SET PYTHON_LIB_PATH=%PYTHON_PATH%\Lib\site-packages
SET PATH=%PYTHON_PATH%;%PYTHON_PATH%\Scripts;%DP0%\CMake\Bin;%PATH%
SET DISTUTILS_USE_SDK=1