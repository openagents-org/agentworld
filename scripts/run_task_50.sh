#!/bin/bash

# Run Task 50 in a screen session

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_DIR="logs/task_50_run_${TIMESTAMP}"
SCREEN_NAME="task_50"

echo "=========================================="
echo "Running Task 50: Combat Battalion - Ogre Hunt"
echo "=========================================="
echo "Output directory: ${OUTPUT_DIR}"
echo "Screen session: ${SCREEN_NAME}"
echo ""

# Kill any existing task_50 screen session
screen -S "${SCREEN_NAME}" -X quit 2>/dev/null

# Create the screen session and run the task
screen -dmS "${SCREEN_NAME}" bash -c "
    cd /Users/yuanyuan/workspace/agentworld
    python agents/run.py \
        --task data_v0.1_multi/v1.3_benchmark/task_50_combat_battalion.yaml \
        --agent agents/configs/openai_agent.yaml \
        --output ${OUTPUT_DIR}
    echo ''
    echo 'Task completed. Press Enter to close this screen session.'
    read
"

echo "Screen session '${SCREEN_NAME}' started."
echo ""
echo "Commands:"
echo "  Attach:  screen -r ${SCREEN_NAME}"
echo "  List:    screen -ls"
echo "  Kill:    screen -S ${SCREEN_NAME} -X quit"
echo ""
