#!/usr/bin/env python3
import subprocess
import time
import signal
import os

def test_detailed_logging():
    print("🚀 Starting detailed logging test...")
    print("   Will run for ~10 seconds then interrupt to show tool calls")
    
    # Start the process
    process = subprocess.Popen([
        'python', 'agents/run.py', 
        '--task', 'data_v0.1_multi/task_1.yaml',
        '--agent', 'agents/configs/qwen_agent.yaml',
        '--output', 'logs_detailed_demo'
    ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
    
    print("⏱️  Letting it run for 10 seconds...")
    time.sleep(10)
    
    print("🛑 Sending interrupt signal...")
    process.send_signal(signal.SIGINT)
    
    # Wait for process to complete
    stdout, _ = process.communicate(timeout=5)
    print("📊 Process completed")
    
    # Show just the round information
    lines = stdout.split('\n')
    showing_round = False
    for line in lines:
        if '🔄 ROUND' in line or '===' in line:
            showing_round = True
            print(line)
        elif showing_round and ('🤖' in line or '🔧' in line or '📊' in line or '💬' in line or '💭' in line):
            print(line)
        elif 'agent_2' in line and 'executing' in line:
            showing_round = False
            print(line)
            break

if __name__ == "__main__":
    test_detailed_logging()
