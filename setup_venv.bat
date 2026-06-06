@echo off
echo Creating Python virtual environment...
python -m venv venv
echo Virtual environment created successfully in the "venv" directory.
echo Activating virtual environment...
call venv\Scripts\activate.bat
cmd /k
