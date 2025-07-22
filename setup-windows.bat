@echo off
REM GitLab Async Mass Exporter - Windows Setup and Run Script

echo ============================================================
echo          GitLab Async Mass Exporter v3.0                 
echo     Exports ALL accessible content from GitLab           
echo ============================================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python 3 is required but not installed.
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

echo Python found: 
python --version

REM Create virtual environment
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
) else (
    echo Virtual environment exists
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo Installing dependencies...
pip install -r requirements-async.txt

REM Check if gitlab_instances.txt exists
if not exist "gitlab_instances.txt" (
    echo Creating gitlab_instances.txt with example data...
    python convert_config.py
)

echo.
echo ============================================================
echo                     READY TO EXPORT                       
echo ============================================================
echo.
echo Starting GitLab Async Mass Exporter...
echo    This will export:
echo    - All projects (with full export archives)
echo    - All groups (preserving structure)
echo    - All wikis
echo    - All snippets
echo    - All issues and merge requests
echo    - Complete metadata
echo.
echo WARNING: This may take a long time for large instances!
echo.

REM Run the exporter
python gitlab_async_tui_exporter.py

REM Deactivate virtual environment
call venv\Scripts\deactivate.bat

echo.
echo Export process completed!
echo Check the 'exports' directory for your data
pause
