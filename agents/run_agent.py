#!/usr/bin/env python3
"""
Quick start script for Qwen AI Agent
"""

import sys
import os

def main():
    """Quick start the agent"""
    print("🎮 Starting Qwen AI Agent for Kaetram...")
    
    # Add current directory to Python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)
    
    try:
        from main import main as main_func
        main_func()
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all dependencies are installed:")
        print("pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 