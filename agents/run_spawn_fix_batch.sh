#!/bin/bash
# Run the 6 spawn location fixed tasks in 6 parallel screens
# Tasks: 84, 90, 91, 92, 95, 99

cd /home/ubuntu/works/agentworld

LOG_DIR="agents/logs/v1.3_spawn_fix"
AGENT_CONFIG="agents/configs/openai_agent.yaml"

mkdir -p "$LOG_DIR"

echo "=============================================="
echo "Running spawn location fixed tasks in 6 parallel screens"
echo "Output directory: $LOG_DIR"
echo "Started at: $(date)"
echo "=============================================="

# Tasks to run
TASKS=(84 90 91 92 95 99)

echo ""
echo ">>> Starting 6 parallel screen sessions..."

# Create a screen for each task
for task_num in "${TASKS[@]}"; do
    TASK_FILE=$(ls data_v0.1_multi/v1.3_benchmark/task_${task_num}_*.yaml 2>/dev/null | head -1)

    if [ -n "$TASK_FILE" ]; then
        screen -dmS spawn_fix_task${task_num} bash -c "
cd /home/ubuntu/works/agentworld
LOG_DIR=\"agents/logs/v1.3_spawn_fix\"
AGENT_CONFIG=\"agents/configs/openai_agent.yaml\"

exec > >(tee -a \"\$LOG_DIR/task_${task_num}.log\") 2>&1

echo ''
echo '>>> Starting Task ${task_num} at \$(date)'
echo 'Task file: ${TASK_FILE}'

python3 agents/run.py \\
    --task \"${TASK_FILE}\" \\
    --agent \"\$AGENT_CONFIG\" \\
    --output \"\$LOG_DIR\" \\
    --no-split-screen

echo '>>> Task ${task_num} completed with exit code \$? at \$(date)'
"
        echo "  Started screen: spawn_fix_task${task_num} for ${TASK_FILE}"
    else
        echo "  WARNING: Could not find task file for task ${task_num}"
    fi

    # Stagger screen starts by 3 seconds
    sleep 3
done

echo ""
echo "=============================================="
echo "6 screen sessions started:"
for task_num in "${TASKS[@]}"; do
    echo "  - spawn_fix_task${task_num}"
done
echo ""
echo "Monitor with:"
for task_num in "${TASKS[@]}"; do
    echo "  screen -r spawn_fix_task${task_num}"
done
echo ""
echo "Or check logs:"
echo "  tail -f $LOG_DIR/task_*.log"
echo ""
echo "Check status:"
echo "  screen -ls"
echo "=============================================="
