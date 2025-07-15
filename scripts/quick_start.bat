@echo off
setlocal enabledelayedexpansion

:: Kaetram API Test Quick Start Script (Windows Version)

echo 🎮 Kaetram API Test Suite Quick Start
echo ==================================

:: Check if Node.js is installed
where node >nul 2>nul
if errorlevel 1 (
    echo ❌ Node.js not installed, please install Node.js first (version >= 16)
    pause
    exit /b 1
)

:: Check if Python is installed
where python >nul 2>nul
if errorlevel 1 (
    echo ❌ Python not installed, please install Python3 first
    pause
    exit /b 1
)

:: Get script directory
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

echo 📁 Current directory: %SCRIPT_DIR%

:: Check configuration file
if not exist "config.json" (
    echo ❌ Configuration file config.json not found
    echo Please configure test parameters according to README.md first
    pause
    exit /b 1
)

:: Choose runtime environment
echo.
echo Please choose runtime environment:
echo 1^) Python (recommended)
echo 2^) JavaScript/Node.js
echo 3^) Both
echo.

set /p choice=Enter your choice (1-3): 

if "%choice%"=="1" (
    echo 🐍 Running Python tests...
    echo Checking Python dependencies...
    
    :: Check if dependencies are installed
    python -c "import requests, colorlog, tabulate" >nul 2>nul
    if errorlevel 1 (
        echo Installing Python dependencies...
        pip install -r requirements.txt
    )
    
    :: Choose test type
    echo.
    echo Choose test type:
    echo 1^) Server API tests only
    echo 2^) Hub API tests only
    echo 3^) AI Agent workflow tests only
    echo 4^) All tests
    echo.
    
    set /p test_choice=Enter your choice (1-4): 
    
    if "!test_choice!"=="1" (
        echo Running Server API tests...
        python python/test_server_api.py
    ) else if "!test_choice!"=="2" (
        echo Running Hub API tests...
        python python/test_hub_api.py
    ) else if "!test_choice!"=="3" (
        echo Running AI Agent workflow tests...
        python python/test_ai_agent.py
    ) else if "!test_choice!"=="4" (
        echo Running all tests...
        python python/run_all_tests.py
    ) else (
        echo Invalid choice, running all tests...
        python python/run_all_tests.py
    )
) else if "%choice%"=="2" (
    echo 🟨 Running JavaScript tests...
    echo Checking Node.js dependencies...
    
    :: Check if dependencies are installed
    if not exist "node_modules" (
        echo Installing Node.js dependencies...
        npm install
    )
    
    echo Running JavaScript tests...
    node javascript/run_all_tests.js
) else if "%choice%"=="3" (
    echo 🔄 Running both Python and JavaScript tests...
    
    :: Install Python dependencies
    python -c "import requests, colorlog, tabulate" >nul 2>nul
    if errorlevel 1 (
        echo Installing Python dependencies...
        pip install -r requirements.txt
    )
    
    :: Install Node.js dependencies
    if not exist "node_modules" (
        echo Installing Node.js dependencies...
        npm install
    )
    
    echo Running Python tests...
    python python/run_all_tests.py
    
    echo.
    echo Running JavaScript tests...
    node javascript/run_all_tests.js
) else (
    echo Invalid choice, running Python tests by default...
    
    :: Install Python dependencies
    python -c "import requests, colorlog, tabulate" >nul 2>nul
    if errorlevel 1 (
        echo Installing Python dependencies...
        pip install -r requirements.txt
    )
    
    python python/run_all_tests.py
)

echo.
echo ✅ Test execution completed!
echo 📊 Check the test_reports/ directory for detailed results
echo 📝 For more information, see README.md

pause 