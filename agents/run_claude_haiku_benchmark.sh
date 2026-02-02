#!/bin/bash
# Run benchmark tasks 1-30 and 75-100 using Claude 3.5 Haiku in 6 parallel screens
# Total: 56 tasks across 6 screens (~9-10 tasks each)

cd /home/ubuntu/works/agentworld

LOG_DIR="agents/logs/claude_haiku_v1.3"
AGENT_CONFIG="agents/configs/claude_agent.yaml"

mkdir -p "$LOG_DIR"

echo "=============================================="
echo "Running v1.3 benchmark with Claude 3.5 Haiku"
echo "Tasks: 1-30, 75-100 (56 total)"
echo "Output directory: $LOG_DIR"
echo "Agent config: $AGENT_CONFIG"
echo "Started at: $(date)"
echo "=============================================="

# Define task ranges for each screen (as start-end)
# Screen 1: tasks 1-10
# Screen 2: tasks 11-20
# Screen 3: tasks 21-30
# Screen 4: tasks 75-84
# Screen 5: tasks 85-93
# Screen 6: tasks 94-100

echo ""
echo ">>> Starting 6 parallel screen sessions..."

# Screen 1: tasks 1-10
screen -dmS claude_haiku_s1 bash -c '
cd /home/ubuntu/works/agentworld
LOG_DIR="agents/logs/claude_haiku_v1.3"
AGENT_CONFIG="agents/configs/claude_agent.yaml"

exec > >(tee -a "$LOG_DIR/screen_1.log") 2>&1

echo "=============================================="
echo "Screen 1 started at $(date)"
echo "Tasks: 01-10"
echo "=============================================="

for task_num in 01 02 03 04 05 06 07 08 09 10; do
    TASK_FILE=$(ls data_v0.1_multi/v1.3_benchmark/task_${task_num}_*.yaml 2>/dev/null | head -1)

    if [ -n "$TASK_FILE" ]; then
        echo ""
        echo ">>> Starting Task $task_num at $(date)"
        echo "Task file: $TASK_FILE"

        python3 agents/run.py \
            --task "$TASK_FILE" \
            --agent "$AGENT_CONFIG" \
            --output "$LOG_DIR" \
            --no-split-screen

        echo ">>> Task $task_num completed with exit code $? at $(date)"
    else
        echo "WARNING: Could not find task file for task $task_num"
    fi
done

echo ""
echo "=============================================="
echo "Screen 1 completed all tasks at $(date)"
echo "=============================================="
'
echo "  Started screen: claude_haiku_s1 for tasks 01-10"
sleep 5

# Screen 2: tasks 11-20
screen -dmS claude_haiku_s2 bash -c '
cd /home/ubuntu/works/agentworld
LOG_DIR="agents/logs/claude_haiku_v1.3"
AGENT_CONFIG="agents/configs/claude_agent.yaml"

exec > >(tee -a "$LOG_DIR/screen_2.log") 2>&1

echo "=============================================="
echo "Screen 2 started at $(date)"
echo "Tasks: 11-20"
echo "=============================================="

for task_num in 11 12 13 14 15 16 17 18 19 20; do
    TASK_FILE=$(ls data_v0.1_multi/v1.3_benchmark/task_${task_num}_*.yaml 2>/dev/null | head -1)

    if [ -n "$TASK_FILE" ]; then
        echo ""
        echo ">>> Starting Task $task_num at $(date)"
        echo "Task file: $TASK_FILE"

        python3 agents/run.py \
            --task "$TASK_FILE" \
            --agent "$AGENT_CONFIG" \
            --output "$LOG_DIR" \
            --no-split-screen

        echo ">>> Task $task_num completed with exit code $? at $(date)"
    else
        echo "WARNING: Could not find task file for task $task_num"
    fi
done

echo ""
echo "=============================================="
echo "Screen 2 completed all tasks at $(date)"
echo "=============================================="
'
echo "  Started screen: claude_haiku_s2 for tasks 11-20"
sleep 5

# Screen 3: tasks 21-30
screen -dmS claude_haiku_s3 bash -c '
cd /home/ubuntu/works/agentworld
LOG_DIR="agents/logs/claude_haiku_v1.3"
AGENT_CONFIG="agents/configs/claude_agent.yaml"

exec > >(tee -a "$LOG_DIR/screen_3.log") 2>&1

echo "=============================================="
echo "Screen 3 started at $(date)"
echo "Tasks: 21-30"
echo "=============================================="

for task_num in 21 22 23 24 25 26 27 28 29 30; do
    TASK_FILE=$(ls data_v0.1_multi/v1.3_benchmark/task_${task_num}_*.yaml 2>/dev/null | head -1)

    if [ -n "$TASK_FILE" ]; then
        echo ""
        echo ">>> Starting Task $task_num at $(date)"
        echo "Task file: $TASK_FILE"

        python3 agents/run.py \
            --task "$TASK_FILE" \
            --agent "$AGENT_CONFIG" \
            --output "$LOG_DIR" \
            --no-split-screen

        echo ">>> Task $task_num completed with exit code $? at $(date)"
    else
        echo "WARNING: Could not find task file for task $task_num"
    fi
done

echo ""
echo "=============================================="
echo "Screen 3 completed all tasks at $(date)"
echo "=============================================="
'
echo "  Started screen: claude_haiku_s3 for tasks 21-30"
sleep 5

# Screen 4: tasks 75-84
screen -dmS claude_haiku_s4 bash -c '
cd /home/ubuntu/works/agentworld
LOG_DIR="agents/logs/claude_haiku_v1.3"
AGENT_CONFIG="agents/configs/claude_agent.yaml"

exec > >(tee -a "$LOG_DIR/screen_4.log") 2>&1

echo "=============================================="
echo "Screen 4 started at $(date)"
echo "Tasks: 75-84"
echo "=============================================="

for task_num in 75 76 77 78 79 80 81 82 83 84; do
    TASK_FILE=$(ls data_v0.1_multi/v1.3_benchmark/task_${task_num}_*.yaml 2>/dev/null | head -1)

    if [ -n "$TASK_FILE" ]; then
        echo ""
        echo ">>> Starting Task $task_num at $(date)"
        echo "Task file: $TASK_FILE"

        python3 agents/run.py \
            --task "$TASK_FILE" \
            --agent "$AGENT_CONFIG" \
            --output "$LOG_DIR" \
            --no-split-screen

        echo ">>> Task $task_num completed with exit code $? at $(date)"
    else
        echo "WARNING: Could not find task file for task $task_num"
    fi
done

echo ""
echo "=============================================="
echo "Screen 4 completed all tasks at $(date)"
echo "=============================================="
'
echo "  Started screen: claude_haiku_s4 for tasks 75-84"
sleep 5

# Screen 5: tasks 85-93
screen -dmS claude_haiku_s5 bash -c '
cd /home/ubuntu/works/agentworld
LOG_DIR="agents/logs/claude_haiku_v1.3"
AGENT_CONFIG="agents/configs/claude_agent.yaml"

exec > >(tee -a "$LOG_DIR/screen_5.log") 2>&1

echo "=============================================="
echo "Screen 5 started at $(date)"
echo "Tasks: 85-93"
echo "=============================================="

for task_num in 85 86 87 88 89 90 91 92 93; do
    TASK_FILE=$(ls data_v0.1_multi/v1.3_benchmark/task_${task_num}_*.yaml 2>/dev/null | head -1)

    if [ -n "$TASK_FILE" ]; then
        echo ""
        echo ">>> Starting Task $task_num at $(date)"
        echo "Task file: $TASK_FILE"

        python3 agents/run.py \
            --task "$TASK_FILE" \
            --agent "$AGENT_CONFIG" \
            --output "$LOG_DIR" \
            --no-split-screen

        echo ">>> Task $task_num completed with exit code $? at $(date)"
    else
        echo "WARNING: Could not find task file for task $task_num"
    fi
done

echo ""
echo "=============================================="
echo "Screen 5 completed all tasks at $(date)"
echo "=============================================="
'
echo "  Started screen: claude_haiku_s5 for tasks 85-93"
sleep 5

# Screen 6: tasks 94-100
screen -dmS claude_haiku_s6 bash -c '
cd /home/ubuntu/works/agentworld
LOG_DIR="agents/logs/claude_haiku_v1.3"
AGENT_CONFIG="agents/configs/claude_agent.yaml"

exec > >(tee -a "$LOG_DIR/screen_6.log") 2>&1

echo "=============================================="
echo "Screen 6 started at $(date)"
echo "Tasks: 94-100"
echo "=============================================="

for task_num in 94 95 96 97 98 99 100; do
    TASK_FILE=$(ls data_v0.1_multi/v1.3_benchmark/task_${task_num}_*.yaml 2>/dev/null | head -1)

    if [ -n "$TASK_FILE" ]; then
        echo ""
        echo ">>> Starting Task $task_num at $(date)"
        echo "Task file: $TASK_FILE"

        python3 agents/run.py \
            --task "$TASK_FILE" \
            --agent "$AGENT_CONFIG" \
            --output "$LOG_DIR" \
            --no-split-screen

        echo ">>> Task $task_num completed with exit code $? at $(date)"
    else
        echo "WARNING: Could not find task file for task $task_num"
    fi
done

echo ""
echo "=============================================="
echo "Screen 6 completed all tasks at $(date)"
echo "=============================================="
'
echo "  Started screen: claude_haiku_s6 for tasks 94-100"

echo ""
echo "=============================================="
echo "6 screen sessions started:"
echo "  - claude_haiku_s1: tasks 01-10"
echo "  - claude_haiku_s2: tasks 11-20"
echo "  - claude_haiku_s3: tasks 21-30"
echo "  - claude_haiku_s4: tasks 75-84"
echo "  - claude_haiku_s5: tasks 85-93"
echo "  - claude_haiku_s6: tasks 94-100"
echo ""
echo "Monitor with:"
echo "  screen -r claude_haiku_s1  (or s2, s3, s4, s5, s6)"
echo ""
echo "Check logs:"
echo "  tail -f $LOG_DIR/screen_*.log"
echo ""
echo "Check status:"
echo "  screen -ls"
echo "=============================================="
