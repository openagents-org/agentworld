#!/bin/bash

# Kaetram API Test Quick Start Script

set -e

echo "🎮 Kaetram API Test Suite Quick Start"
echo "=================================="

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not installed, please install Node.js first (version >= 16)"
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not installed, please install Python3 first"
    exit 1
fi

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "📁 Current directory: $SCRIPT_DIR"

# Check configuration file
if [ ! -f "config.json" ]; then
    echo "❌ Configuration file config.json not found"
    echo "Please configure test parameters according to README.md first"
    exit 1
fi

# Choose runtime environment
echo ""
echo "Please choose runtime environment:"
echo "1) Python (recommended)"
echo "2) JavaScript/Node.js"
echo "3) Both"
echo ""

read -p "Enter your choice (1-3): " choice

case $choice in
    1)
        echo "🐍 Running Python tests..."
        echo "Checking Python dependencies..."
        
        # Check if dependencies are installed
        if ! python3 -c "import requests, colorlog, tabulate" &> /dev/null; then
            echo "Installing Python dependencies..."
            pip3 install -r requirements.txt
        fi
        
        # Choose test type
        echo ""
        echo "Choose test type:"
        echo "1) Server API tests only"
        echo "2) Hub API tests only"
        echo "3) AI Agent workflow tests only"
        echo "4) All tests"
        echo ""
        
        read -p "Enter your choice (1-4): " test_choice
        
        case $test_choice in
            1)
                echo "Running Server API tests..."
                python3 python/test_server_api.py
                ;;
            2)
                echo "Running Hub API tests..."
                python3 python/test_hub_api.py
                ;;
            3)
                echo "Running AI Agent workflow tests..."
                python3 python/test_ai_agent.py
                ;;
            4)
                echo "Running all tests..."
                python3 python/run_all_tests.py
                ;;
            *)
                echo "Invalid choice, running all tests..."
                python3 python/run_all_tests.py
                ;;
        esac
        ;;
    2)
        echo "🟨 Running JavaScript tests..."
        echo "Checking Node.js dependencies..."
        
        # Check if dependencies are installed
        if [ ! -d "node_modules" ]; then
            echo "Installing Node.js dependencies..."
            npm install
        fi
        
        echo "Running JavaScript tests..."
        node javascript/run_all_tests.js
        ;;
    3)
        echo "🔄 Running both Python and JavaScript tests..."
        
        # Install Python dependencies
        if ! python3 -c "import requests, colorlog, tabulate" &> /dev/null; then
            echo "Installing Python dependencies..."
            pip3 install -r requirements.txt
        fi
        
        # Install Node.js dependencies
        if [ ! -d "node_modules" ]; then
            echo "Installing Node.js dependencies..."
            npm install
        fi
        
        echo "Running Python tests..."
        python3 python/run_all_tests.py
        
        echo ""
        echo "Running JavaScript tests..."
        node javascript/run_all_tests.js
        ;;
    *)
        echo "Invalid choice, running Python tests by default..."
        
        # Install Python dependencies
        if ! python3 -c "import requests, colorlog, tabulate" &> /dev/null; then
            echo "Installing Python dependencies..."
            pip3 install -r requirements.txt
        fi
        
        python3 python/run_all_tests.py
        ;;
esac

echo ""
echo "✅ Test execution completed!"
echo "📊 Check the test_reports/ directory for detailed results"
echo "📝 For more information, see README.md" 