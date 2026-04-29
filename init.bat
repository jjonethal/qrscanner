@echo off
setlocal

:: Check if virtual environment exists
if not exist qrenv\Scripts\activate.bat call :init_env

:: Activate virtual environment
call qrenv\Scripts\activate.bat

:: Run the application
python qrscanner.py

goto :eof

:init_env
echo Creating virtual environment...
python -m venv qrenv || ( echo Error: Failed to create python environment & exit /b 1 )
echo Installing dependencies...
call qrenv\Scripts\activate.bat
pip install -r requirements.txt
exit /b 0
