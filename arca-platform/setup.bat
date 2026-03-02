@echo off
REM ARCA Platform - Quick Start Script for Windows

echo ==================================
echo ARCA Platform - Quick Start
echo ==================================
echo.

REM Check prerequisites
echo Checking prerequisites...

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python 3 is not installed
    exit /b 1
)
echo ✅ Python found

REM Check Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is not installed
    exit /b 1
)
echo ✅ Node.js found

echo.
echo ==================================
echo Setting up Backend...
echo ==================================

cd backend

REM Create virtual environment
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate

REM Install dependencies
echo Installing Python dependencies...
pip install -r requirements.txt

REM Copy env file if not exists
if not exist ".env" (
    echo Creating .env file...
    copy .env.example .env
    echo ⚠️  Please edit backend\.env with your configuration
)

cd ..

echo.
echo ==================================
echo Setting up Frontend...
echo ==================================

cd frontend

REM Install dependencies
if not exist "node_modules" (
    echo Installing Node dependencies...
    call npm install
)

REM Create env file if not exists
if not exist ".env" (
    echo Creating frontend .env file...
    echo VITE_API_URL=http://localhost:5000/api > .env
)

cd ..

echo.
echo ==================================
echo ✅ Setup Complete!
echo ==================================
echo.
echo To start the platform:
echo.
echo 1. Start Backend:
echo    cd backend
echo    venv\Scripts\activate
echo    python app.py
echo.
echo 2. Start Frontend (in new terminal):
echo    cd frontend
echo    npm run dev
echo.
echo 3. Open browser:
echo    http://localhost:3000
echo.
echo ==================================

pause
