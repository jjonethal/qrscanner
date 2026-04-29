@echo off
setlocal

:: Check if virtual environment exists
if not exist qrenv\Scripts\activate.bat call :init_env || ( echo error installing python environment )

:: Activate virtual environment
call qrenv\Scripts\activate.bat

:: Run the application
python qrscanner.py %*

goto :eof

:init_env
echo Creating virtual environment...
python -m venv qrenv || ( echo Error: Failed to create python environment & exit /b 1 )
echo Installing dependencies...
call qrenv\Scripts\activate.bat
python -m pip install  -U pip || ( echo error updating pip & exit /b 1 )
pip install -r requirements.txt
exit /b 0
