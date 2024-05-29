REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Python is not installed. Please install Python first.
    pause
    exit /b 1
)

REM Create a virtual environment
python -m venv pythonEnv

REM Activate the virtual environment
call pythonEnv\Scripts\activate

REM Install dependencies from requirements.txt
if exist requirements.txt (
    pip install -r requirements.txt
) else (
    echo requirements.txt not found. Please ensure the file is in the project directory.
    call venv\Scripts\deactivate
    pause
    exit /b 1
)

REM Inform the user that setup is complete
echo Setup complete. The virtual environment is ready to use.
pause
