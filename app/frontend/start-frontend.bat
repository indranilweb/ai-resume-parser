@echo off
echo Starting AI Resume Parser Frontend (React + Vite)
echo =====================================================
cd /d "%~dp0"
echo Current directory: %CD%
echo.
echo Installing dependencies (if needed)...
call npm install
echo.
echo Starting development server...
echo Frontend will be available at: http://localhost:3000
echo Backend should be running at: http://localhost:8000
echo.
call npm run dev
pause
