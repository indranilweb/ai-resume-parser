@echo off
echo Setting up AI Resume Parser...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and add it to your PATH
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js and npm
    pause
    exit /b 1
)

echo Python and Node.js found. Proceeding with setup...
echo.

REM Navigate to backend folder
cd app\backend

REM Create Python virtual environment
echo Creating Python virtual environment in backend folder...
if exist "venv" (
    echo Virtual environment already exists. Removing old one...
    rmdir /s /q venv
)

python -m venv venv
if %errorlevel% neq 0 (
    echo ERROR: Failed to create virtual environment
    cd ..\..
    pause
    exit /b 1
)

echo Virtual environment created successfully.
echo.

REM Activate virtual environment and install backend requirements
echo Activating virtual environment and installing backend requirements...
call venv\Scripts\activate.bat

REM Upgrade pip first
python -m pip install --upgrade pip

REM Install backend requirements
pip install -r ..\..\requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install backend requirements
    cd ..\..
    pause
    exit /b 1
)

echo Backend requirements installed successfully.
echo.

REM Return to root for frontend setup
cd ..\..

REM Install frontend dependencies
echo Installing frontend dependencies...
cd app\frontend

npm install
if %errorlevel% neq 0 (
    echo ERROR: Failed to install frontend dependencies
    cd ..\..
    pause
    exit /b 1
)

echo Frontend dependencies installed successfully.
echo.

REM Return to root directory
cd ..\..

echo.
echo ============================================
echo Setup completed successfully!
echo ============================================
echo.
echo To start the application:
echo 1. Backend: Run start.bat (or manually activate venv and run python app/backend/api_server.py)
echo 2. Frontend: Run app/frontend/start-frontend.bat (or cd app/frontend && npm run dev)
echo.
echo Virtual environment location: %cd%\app\backend\venv
echo To activate manually: app\backend\venv\Scripts\activate.bat
echo.
pause
