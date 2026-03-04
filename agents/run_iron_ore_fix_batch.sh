#!/bin/bash
# Run the 8 iron ore fixed tasks in 3 parallel screens
# Tasks: 78, 82, 84, 86, 87, 93, 98, 100

cd /home/ubuntu/works/agentworld

LOG_DIR="agents/logs/v1.3_iron_ore_fix"
AGENT_CONFIG="agents/configs/openai_agent.yaml"

mkdir -p "$LOG_DIR"

echo "=============================================="
echo "Running iron ore fixed tasks in parallel"
echo "Output directory: $LOG_DIR"
echo "Started at: $(date)"
echo "=============================================="

# First, add task-specific prefixes to usernames to avoid login conflicts
echo ""
echo ">>> Adding task prefixes to usernames to avoid login conflicts..."

for task_num in 78 82 84 86 87 93 98 100; do
    TASK_FILE=$(ls data_v0.1_multi/v1.3_benchmark/task_${task_num}_*.yaml 2>/dev/null | head -1)
    if [ -n "$TASK_FILE" ]; then
        # Create backup if not already exists
        if [ ! -f "${TASK_FILE}.backup" ]; then
            cp "$TASK_FILE" "${TASK_FILE}.backup"
        fi

        # Check if already has prefix
        if grep -q "username: t${task_num}_" "$TASK_FILE"; then
            echo "  Task $task_num: Already has t${task_num}_ prefix"
        else
            # Add task prefix to all usernames (e.g., logger1_agent -> t78_logger1_agent)
            sed -i "s/username: /username: t${task_num}_/g" "$TASK_FILE"
            echo "  Task $task_num: Added t${task_num}_ prefix to usernames"
        fi
    fi
done

echo ""
echo ">>> Starting 3 parallel screen sessions..."

# Screen 1: Tasks 78, 86, 100
screen -dmS iron_fix_screen1 bash -c '
cd /home/ubuntu/works/agentworld
LOG_DIR="agents/logs/v1.3_iron_ore_fix"
AGENT_CONFIG="agents/configs/openai_agent.yaml"

exec > >(tee -a "$LOG_DIR/screen1.log") 2>&1

for task_num in 78 86 100; do
    echo ""
    echo ">>> [Screen 1] Starting Task $task_num at $(date)"
    TASK_FILE=$(ls data_v0.1_multi/v1.3_benchmark/task_${task_num}_*.yaml 2>/dev/null | head -1)

    if [ -n "$TASK_FILE" ]; then
        python3 agents/run.py \
            --task "$TASK_FILE" \
            --agent "$AGENT_CONFIG" \
            --output "$LOG_DIR" \
            --no-split-screen
        echo "  [Screen 1] Task $task_num completed with exit code $?"
    fi
    sleep 3
done
echo "[Screen 1] All tasks completed at $(date)"
'

sleep 5  # Stagger screen starts

# Screen 2: Tasks 82, 87, 98
screen -dmS iron_fix_screen2 bash -c '
cd /home/ubuntu/works/agentworld
LOG_DIR="agents/logs/v1.3_iron_ore_fix"
AGENT_CONFIG="agents/configs/openai_agent.yaml"

exec > >(tee -a "$LOG_DIR/screen2.log") 2>&1

for task_num in 82 87 98; do
    echo ""
    echo ">>> [Screen 2] Starting Task $task_num at $(date)"
    TASK_FILE=$(ls data_v0.1_multi/v1.3_benchmark/task_${task_num}_*.yaml 2>/dev/null | head -1)

    if [ -n "$TASK_FILE" ]; then
        python3 agents/run.py \
            --task "$TASK_FILE" \
            --agent "$AGENT_CONFIG" \
            --output "$LOG_DIR" \
            --no-split-screen
        echo "  [Screen 2] Task $task_num completed with exit code $?"
    fi
    sleep 3
done
echo "[Screen 2] All tasks completed at $(date)"
'

sleep 5  # Stagger screen starts

# Screen 3: Tasks 84, 93
screen -dmS iron_fix_screen3 bash -c '
cd /home/ubuntu/works/agentworld
LOG_DIR="agents/logs/v1.3_iron_ore_fix"
AGENT_CONFIG="agents/configs/openai_agent.yaml"

exec > >(tee -a "$LOG_DIR/screen3.log") 2>&1

for task_num in 84 93; do
    echo ""
    echo ">>> [Screen 3] Starting Task $task_num at $(date)"
    TASK_FILE=$(ls data_v0.1_multi/v1.3_benchmark/task_${task_num}_*.yaml 2>/dev/null | head -1)

    if [ -n "$TASK_FILE" ]; then
        python3 agents/run.py \
            --task "$TASK_FILE" \
            --agent "$AGENT_CONFIG" \
            --output "$LOG_DIR" \
            --no-split-screen
        echo "  [Screen 3] Task $task_num completed with exit code $?"
    fi
    sleep 3
done
echo "[Screen 3] All tasks completed at $(date)"
'

echo ""
echo "=============================================="
echo "3 screen sessions started:"
echo "  - iron_fix_screen1: Tasks 78, 86, 100"
echo "  - iron_fix_screen2: Tasks 82, 87, 98"
echo "  - iron_fix_screen3: Tasks 84, 93"
echo ""
echo "Monitor with:"
echo "  screen -r iron_fix_screen1"
echo "  screen -r iron_fix_screen2"
echo "  screen -r iron_fix_screen3"
echo ""
echo "Or check logs:"
echo "  tail -f $LOG_DIR/screen*.log"
echo ""
echo "Check status:"
echo "  screen -ls"
echo "=============================================="
