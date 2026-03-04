#!/bin/bash
# Run benchmark tasks 31-45 using GPT-5-mini in 6 parallel screens
# Total: 15 tasks across 6 screens (~2-3 tasks each)

cd /home/ubuntu/works/agentworld

LOG_DIR="agents/logs/gpt5mini_tasks31_45"
AGENT_CONFIG="agents/configs/openai_agent.yaml"

mkdir -p "$LOG_DIR"

echo "=============================================="
echo "Running tasks 31-45 with GPT-5-mini"
echo "Tasks: 31-45 (15 total)"
echo "Output directory: $LOG_DIR"
echo "Agent config: $AGENT_CONFIG"
echo "Started at: $(date)"
echo "=============================================="

echo ""
echo ">>> Starting 6 parallel screen sessions..."

# Screen 1: tasks 31-32
screen -dmS gpt5_s1 bash -c '
cd /home/ubuntu/works/agentworld
LOG_DIR="agents/logs/gpt5mini_tasks31_45"
AGENT_CONFIG="agents/configs/openai_agent.yaml"

exec > >(tee -a "$LOG_DIR/screen_1.log") 2>&1

echo "=============================================="
echo "Screen 1 started at $(date)"
echo "Tasks: 31-32"
echo "=============================================="

for task_num in 31 32; do
    TASK_FILE=$(ls data_v0.1_multi/v1.3_benchmark/task_${task_num}_*.yaml 2>/dev/null | head -1)
    if [ -n "$TASK_FILE" ]; then
        echo ""
        echo ">>> Starting Task $task_num at $(date)"
        python3 agents/run.py --task "$TASK_FILE" --agent "$AGENT_CONFIG" --output "$LOG_DIR" --no-split-screen
        echo ">>> Task $task_num completed with exit code $? at $(date)"
    fi
done
echo "Screen 1 completed at $(date)"
'
echo "  Started screen: gpt5_s1 for tasks 31-32"
sleep 3

# Screen 2: tasks 33-34
screen -dmS gpt5_s2 bash -c '
cd /home/ubuntu/works/agentworld
LOG_DIR="agents/logs/gpt5mini_tasks31_45"
AGENT_CONFIG="agents/configs/openai_agent.yaml"

exec > >(tee -a "$LOG_DIR/screen_2.log") 2>&1

echo "=============================================="
echo "Screen 2 started at $(date)"
echo "Tasks: 33-34"
echo "=============================================="

for task_num in 33 34; do
    TASK_FILE=$(ls data_v0.1_multi/v1.3_benchmark/task_${task_num}_*.yaml 2>/dev/null | head -1)
    if [ -n "$TASK_FILE" ]; then
        echo ""
        echo ">>> Starting Task $task_num at $(date)"
        python3 agents/run.py --task "$TASK_FILE" --agent "$AGENT_CONFIG" --output "$LOG_DIR" --no-split-screen
        echo ">>> Task $task_num completed with exit code $? at $(date)"
    fi
done
echo "Screen 2 completed at $(date)"
'
echo "  Started screen: gpt5_s2 for tasks 33-34"
sleep 3

# Screen 3: tasks 35-36
screen -dmS gpt5_s3 bash -c '
cd /home/ubuntu/works/agentworld
LOG_DIR="agents/logs/gpt5mini_tasks31_45"
AGENT_CONFIG="agents/configs/openai_agent.yaml"

exec > >(tee -a "$LOG_DIR/screen_3.log") 2>&1

echo "=============================================="
echo "Screen 3 started at $(date)"
echo "Tasks: 35-36"
echo "=============================================="

for task_num in 35 36; do
    TASK_FILE=$(ls data_v0.1_multi/v1.3_benchmark/task_${task_num}_*.yaml 2>/dev/null | head -1)
    if [ -n "$TASK_FILE" ]; then
        echo ""
        echo ">>> Starting Task $task_num at $(date)"
        python3 agents/run.py --task "$TASK_FILE" --agent "$AGENT_CONFIG" --output "$LOG_DIR" --no-split-screen
        echo ">>> Task $task_num completed with exit code $? at $(date)"
    fi
done
echo "Screen 3 completed at $(date)"
'
echo "  Started screen: gpt5_s3 for tasks 35-36"
sleep 3

# Screen 4: tasks 37-38
screen -dmS gpt5_s4 bash -c '
cd /home/ubuntu/works/agentworld
LOG_DIR="agents/logs/gpt5mini_tasks31_45"
AGENT_CONFIG="agents/configs/openai_agent.yaml"

exec > >(tee -a "$LOG_DIR/screen_4.log") 2>&1

echo "=============================================="
echo "Screen 4 started at $(date)"
echo "Tasks: 37-38"
echo "=============================================="

for task_num in 37 38; do
    TASK_FILE=$(ls data_v0.1_multi/v1.3_benchmark/task_${task_num}_*.yaml 2>/dev/null | head -1)
    if [ -n "$TASK_FILE" ]; then
        echo ""
        echo ">>> Starting Task $task_num at $(date)"
        python3 agents/run.py --task "$TASK_FILE" --agent "$AGENT_CONFIG" --output "$LOG_DIR" --no-split-screen
        echo ">>> Task $task_num completed with exit code $? at $(date)"
    fi
done
echo "Screen 4 completed at $(date)"
'
echo "  Started screen: gpt5_s4 for tasks 37-38"
sleep 3

# Screen 5: tasks 39-41
screen -dmS gpt5_s5 bash -c '
cd /home/ubuntu/works/agentworld
LOG_DIR="agents/logs/gpt5mini_tasks31_45"
AGENT_CONFIG="agents/configs/openai_agent.yaml"

exec > >(tee -a "$LOG_DIR/screen_5.log") 2>&1

echo "=============================================="
echo "Screen 5 started at $(date)"
echo "Tasks: 39-41"
echo "=============================================="

for task_num in 39 40 41; do
    TASK_FILE=$(ls data_v0.1_multi/v1.3_benchmark/task_${task_num}_*.yaml 2>/dev/null | head -1)
    if [ -n "$TASK_FILE" ]; then
        echo ""
        echo ">>> Starting Task $task_num at $(date)"
        python3 agents/run.py --task "$TASK_FILE" --agent "$AGENT_CONFIG" --output "$LOG_DIR" --no-split-screen
        echo ">>> Task $task_num completed with exit code $? at $(date)"
    fi
done
echo "Screen 5 completed at $(date)"
'
echo "  Started screen: gpt5_s5 for tasks 39-41"
sleep 3

# Screen 6: tasks 42-45
screen -dmS gpt5_s6 bash -c '
cd /home/ubuntu/works/agentworld
LOG_DIR="agents/logs/gpt5mini_tasks31_45"
AGENT_CONFIG="agents/configs/openai_agent.yaml"

exec > >(tee -a "$LOG_DIR/screen_6.log") 2>&1

echo "=============================================="
echo "Screen 6 started at $(date)"
echo "Tasks: 42-45"
echo "=============================================="

for task_num in 42 43 44 45; do
    TASK_FILE=$(ls data_v0.1_multi/v1.3_benchmark/task_${task_num}_*.yaml 2>/dev/null | head -1)
    if [ -n "$TASK_FILE" ]; then
        echo ""
        echo ">>> Starting Task $task_num at $(date)"
        python3 agents/run.py --task "$TASK_FILE" --agent "$AGENT_CONFIG" --output "$LOG_DIR" --no-split-screen
        echo ">>> Task $task_num completed with exit code $? at $(date)"
    fi
done
echo "Screen 6 completed at $(date)"
'
echo "  Started screen: gpt5_s6 for tasks 42-45"

echo ""
echo "=============================================="
echo "6 screen sessions started:"
echo "  - gpt5_s1: tasks 31-32"
echo "  - gpt5_s2: tasks 33-34"
echo "  - gpt5_s3: tasks 35-36"
echo "  - gpt5_s4: tasks 37-38"
echo "  - gpt5_s5: tasks 39-41"
echo "  - gpt5_s6: tasks 42-45"
echo ""
echo "Monitor: screen -r gpt5_s1"
echo "Logs: tail -f $LOG_DIR/screen_*.log"
echo "=============================================="
